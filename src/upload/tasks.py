from __future__ import absolute_import
from __future__ import unicode_literals

import base64
from io import BytesIO
import re

import boto3
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from PIL import Image
import tmdbsimple as tmdb

# If you want to print, you need to log these and they will appear in the celery terminal process

logger = get_task_logger(__name__)


@shared_task
def async_upload_image(image_data, img_filename):
    logger.info("hello world")

    img_str = re.sub("^data:image/.+;base64,", "", image_data)
    img_data = base64.b64decode(img_str)
    img = Image.open(BytesIO(img_data))
    img_temploc = "tmp/" + img_filename
    img.save(img_temploc)

    s3_client = boto3.client("s3")
    s3_client.upload_file(img_temploc, settings.S3_BUCKET, f"image/{img_filename}")
    s3_resource = boto3.resource("s3")
    object_acl = s3_resource.ObjectAcl(settings.S3_BUCKET, f"image/{img_filename}")
    object_acl.put(ACL="public-read")
    return
