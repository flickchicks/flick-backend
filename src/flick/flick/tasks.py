# Create your tasks here
from __future__ import absolute_import, unicode_literals

import base64
import json
import os
import random
import re
import string
from io import BytesIO

import boto3
from asset.models import Asset, AssetBundle
from celery import shared_task
from django.conf import settings
from PIL import Image
from rest_framework import status
from rest_framework.response import Response

# from demoapp.models import Widget


def upload_image(asset_id, salt, img, img_format, kind, width, height):
    # secure way of generating a random string
    img_filename = f"{salt}_{kind}.{img_format}"
    img_temploc = f"{settings.TEMP_DIR}/{img_filename}"
    img.save(img_temploc)

    s3_client = boto3.client("s3")
    s3_client.upload_file(img_temploc, settings.S3_BUCKET, f"image/{img_filename}")

    s3_resource = boto3.resource("s3")
    # make s3 image url public
    object_acl = s3_resource.ObjectAcl(settings.S3_BUCKET, f"image/{img_filename}")
    response = object_acl.put(ACL="public-read")
    print(f"response:{response}")

    asset = Asset.objects.get(pk=asset_id)
    asset.width = width
    asset.height = height
    # asset.extension = img_format
    # asset.processing = False
    asset.save()

    os.remove(img_temploc)
    return


@shared_task
def resize_and_upload(img_str, img_format, salt, kind, asset_id):
    img_data = base64.b64decode(img_str)

    # get PIL image
    img = Image.open(BytesIO(img_data))

    # img_format = img.format.lower()

    if img_format not in ["jpeg", "jpg", "png", "gif"]:
        return Response(
            {"error": "Image type not accepted. Must be jpeg, jpg, png, or gif."},
            status=status.HTTP_400_BAD_REQUEST,
        )

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
    upload_image(asset_id, salt, new_img, img_format, kind, width, height)
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


# @shared_task
# def count_widgets():
#     return Widget.objects.count()


# @shared_task
# def rename_widget(widget_id, name):
#     w = Widget.objects.get(id=widget_id)
#     w.name = name
#     w.save()
