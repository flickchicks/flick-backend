from django.conf import settings

from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api import settings as api_settings
from api.generics import generics
from api.utils import failure_response, success_response
from asset.models import Asset, AssetBundle
from flick.tasks import add, resize_and_upload
from item.models import Item
from item.serializers import ItemDetailSerializer

import base64
import boto3
from io import BytesIO
import json
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string


def upload_image(image_data, user):
    print("UPLOADING IMAGE")
    try:
        # [1:] strips off leading period
        img_ext = guess_extension(guess_type(image_data)[0])[1:]

        if img_ext not in ["jpeg", "jpg", "png", "gif"]:
            return failure_response(
                "Image type not accepted. Must be jpeg, jpg, png, or gif.", status=status.HTTP_400_BAD_REQUEST
            )

        # remove header of base64 string
        img_str = re.sub("^data:image/.+;base64,", "", image_data)

        # secure way of generating random string for image name
        salt = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

        asset_bundle = AssetBundle()
        asset_bundle.salt = salt
        asset_bundle.kind = "image"
        asset_bundle.base_url = settings.S3_BASE_URL
        asset_bundle.owner = user
        asset_bundle.save()

        for kind, _ in Asset.KIND_CHOICES:
            asset = Asset()
            asset.asset_bundle = asset_bundle
            asset.kind = kind
            asset.extension = img_ext
            asset.is_processing = True
            asset.save()

            # do resize_and_upload asynchronously, move onto responding to client
            resize_and_upload.delay(asset.id, salt, img_str, kind, img_ext)

        return asset_bundle
    except Exception as e:
        return failure_response(f"Unable to upload image because of {e}.")
