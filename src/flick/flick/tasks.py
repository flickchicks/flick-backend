from __future__ import absolute_import
from __future__ import unicode_literals

import base64
from io import BytesIO
import os

from asset.models import Asset
import boto3
from celery import shared_task
from django.conf import settings
from imdb import IMDb
from PIL import Image
from provider.models import Provider
from show.models import Show
from show.tmdb_api_utils import TMDB_API
from tag.models import Tag
import tmdbsimple as tmdb


# If you want to print, you need to log these and they will appear in the celery terminal process
# from celery.utils.log import get_task_logger
# logger = get_task_logger(__name__)


def upload_image(asset_id, salt, img, kind, img_ext, width, height):
    # save image in temp dir
    img_filename = f"{salt}_{kind}.{img_ext}"
    img_temploc = f"{settings.TEMP_DIR}/{img_filename}"
    img.save(img_temploc)

    # upload image to S3
    s3_client = boto3.client("s3")
    s3_client.upload_file(img_temploc, settings.S3_BUCKET, f"image/{img_filename}")

    # make S3 image url public
    s3_resource = boto3.resource("s3")
    object_acl = s3_resource.ObjectAcl(settings.S3_BUCKET, f"image/{img_filename}")
    object_acl.put(ACL="public-read")

    # save image details to database
    asset = Asset.objects.get(pk=asset_id)
    asset.width = width
    asset.height = height
    asset.is_processing = False
    asset.save()

    os.remove(img_temploc)
    return


@shared_task
def resize_and_upload(asset_id, salt, img_str, kind, img_ext):
    # get PIL image
    img_data = base64.b64decode(img_str)
    img = Image.open(BytesIO(img_data))

    aspect = img.width / img.height
    width, height = 0, 0
    new_img = img

    if kind == "original":
        width = img.width
        height = img.height
    elif kind == "large":
        width = 1024
        height = int(aspect * 1024)
        new_img = new_img.resize((width, height))
    elif kind == "small":
        width = 128
        height = int(aspect * 128)
        new_img = new_img.resize((width, height))
    else:
        print(f"error: image {kind} not handled yet!")

    upload_image(asset_id, salt, new_img, kind, img_ext, width, height)

    return


@shared_task
def populate_show_details(show_id):
    show = Show.objects.filter(id=show_id)
    if not show:
        return
    show = Show.objects.get(id=show_id)
    if show.ext_api_source == "animelist":
        return
    tmdb_api = TMDB_API()
    imdb_api = IMDb()
    info = None
    if show.is_tv:
        info = tmdb_api.get_tv_info_from_id(show.ext_api_id)
    else:
        info = tmdb_api.get_movie_info_from_id(show.ext_api_id)
    if not info:
        return
    show.directors = info.get("directors")
    show.cast = info.get("cast")
    if info.get("ext_api_genres"):
        for tag in info.get("ext_api_genres"):
            try:
                show.tags.create(
                    name=tag.get("name"), ext_api_genre_id=tag.get("id"), ext_api_source=info.get("ext_api_source")
                )
            except:
                show.tags.add(Tag.objects.get(name=tag.get("name")))
    if info.get("providers"):
        for provider in info.get("providers"):
            try:
                show.providers.create(name=provider.get("name"), image=provider.get("image"))
            except:
                show.providers.add(Provider.objects.get(name=provider.get("name")))
    imdb_id = info.get("imdb_id")
    if imdb_id:
        imdb_id = imdb_id[2:]
        imdb_rating = imdb_api.get_movie(imdb_id).get("rating")
        show.imdb_rating = imdb_rating
    show.save()
