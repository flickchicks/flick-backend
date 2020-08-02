from __future__ import absolute_import
from __future__ import unicode_literals

import base64
from io import BytesIO
import os

from asset.models import Asset
import boto3
from celery import shared_task
from django.conf import settings
from PIL import Image
from show.models import Show
from show.tmdb_api_utils import TMDB_API
from tag.models import Tag
import tmdbsimple as tmdb


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
def add_tags_and_cast(show_id):
    print("reaching add tags and cast")
    show = Show.objects.filter(id=show_id)
    if not show:
        return
    show = Show.objects.get(id=show_id)
    if show.ext_api_source == "animelist":
        print("animelist not supported yet to add tags and cast")
        return
    api = TMDB_API()
    if show.is_tv:
        print("show is tv")
        info = api.get_tv_info_from_id(show.ext_api)
    else:
        info = api.get_movie_info_from_id(show.ext_api)
        print("show is movie", info)
    show.directors = info.get("directors")
    show.cast = info.get("cast")
    if info.get("show_tags"):
        for genre in info.get("show_tags"):
            try:
                show.tags.create(
                    tag=genre.get("name"), ext_api_id=genre.get("id"), ext_api_source=info.get("ext_api_source")
                )
            except:
                show.tags.add(Tag.objects.get(tag=genre.get("name")))
    show.save()
