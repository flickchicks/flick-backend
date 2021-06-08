from __future__ import absolute_import
from __future__ import unicode_literals

import base64
from io import BytesIO
import re

import boto3
from celery import shared_task
from django.conf import settings
import tmdbsimple as tmdb

# If you want to print, you need to log these and they will appear in the celery terminal process
# from celery.utils.log import get_task_logger
# logger = get_task_logger(__name__)
# logger.info("hello world")


@shared_task
def async_upload_image(image_data, img_filename):
    img_str = re.sub("^data:image/.+;base64,", "", image_data)
    img_data = base64.b64decode(img_str)

    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=settings.SPACES_REGION_NAME,
        endpoint_url=settings.SPACES_ENDPOINT_URL,
        aws_access_key_id=settings.SPACES_ACCESS_KEY_ID,
        aws_secret_access_key=settings.SPACES_SECRET_ACCESS_KEY,
    )

    client.put_object(
        Bucket=settings.SPACES_BUCKET_NAME,
        Key=img_filename,
        Body=BytesIO(img_data),
        ACL="public-read",
    )
    return
