from __future__ import absolute_import
from __future__ import unicode_literals

import base64
from io import BytesIO

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from imdb import IMDb
from PIL import Image
from provider.models import Provider
from show.animelist import flickanimelist
from show.models import Show
from show.tmdb import flicktmdb
from tag.models import Tag
import tmdbsimple as tmdb


# If you want to print, you need to log these and they will appear in the celery terminal process

logger = get_task_logger(__name__)
# logger.info("hello world")


@shared_task
def async_upload_image(salt, img_str, img_ext):
    # get PIL image
    logger.info("hello world")
    img_data = base64.b64decode(img_str)
    img = Image.open(BytesIO(img_data))

    img_filename = f"{salt}.{img_ext}"
    img_temploc = f"{settings.TEMP_DIR}/{img_filename}"
    img.save(img_temploc)

    # upload image to S3
    # s3_client = boto3.client("s3")
    # res = s3_client.upload_file(img_temploc, settings.S3_BUCKET, f"image/{img_filename}")
    # logger.info("res", res)

    # # make S3 image url public
    # s3_resource = boto3.resource("s3")
    # object_acl = s3_resource.ObjectAcl(settings.S3_BUCKET, f"image/{img_filename}")
    # object_acl.put(ACL="public-read")
    # logger.info("asdfasdfs")

    # os.remove(img_temploc)
    return


@shared_task
def populate_show_details(show_id):
    show = Show.objects.filter(id=show_id)
    if not show:
        return
    show = Show.objects.get(id=show_id)
    imdb_api = IMDb()
    info = None
    if show.ext_api_source == "tmdb" and show.is_tv is True:
        info = flicktmdb().get_show(show.ext_api_id, is_tv=True)
    elif show.ext_api_source == "tmdb" and show.is_tv is False:
        info = flicktmdb().get_show(show.ext_api_id, is_tv=False)
    elif show.ext_api_source == "animelist":
        info = flickanimelist().get_anime(show.ext_api_id)
    if not info:
        return
    show.cast = info.get("cast")
    show.directors = info.get("directors")
    show.duration = info.get("duration")
    show.seasons = info.get("seasons")
    show.status = info.get("status")
    show.episodes = info.get("episodes")
    show.date_released = info.get("date_released")
    show.animelist_rating = info.get("animelist_rating")
    show.animelist_rank = info.get("animelist_rank")
    show.save()

    if info.get("ext_api_genres") and show.ext_api_source == "tmdb":
        for tag in info.get("ext_api_genres"):
            try:
                show.tags.create(
                    name=tag.get("name") or tag,
                    ext_api_genre_id=tag.get("id"),
                    ext_api_source=info.get("ext_api_source"),
                )
            except:
                show.tags.add(Tag.objects.get(name=tag.get("name") or tag))
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
