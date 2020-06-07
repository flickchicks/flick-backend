from __future__ import absolute_import, unicode_literals

from django.conf import settings

from rest_framework import status
from rest_framework.response import Response

from asset.models import Asset, AssetBundle

import base64
import boto3
from celery import shared_task
from io import BytesIO
import json
import os
from PIL import Image
import random
import re
import string


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
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
