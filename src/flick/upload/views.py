from django.conf import settings

from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from .utils import upload_image
from api import settings as api_settings
from api.generics import generics
from api.utils import failure_response, success_response
from asset.models import Asset, AssetBundle
from flick.tasks import add, resize_and_upload
from item.models import Item
from item.serializers import ItemDetailSerializer

import base64
import boto3
import json
import os
from PIL import Image
import random
import re
import string
from io import BytesIO
from mimetypes import guess_extension, guess_type


class UploadImage(generics.CreateAPIView):

    serializer_class = Serializer

    def post(self, request):
        data = json.loads(request.body)
        if "image" not in data:
            return failure_response("No image in request.")
        asset_bundle = upload_image(data["image"], request.user)
        if not asset_bundle:
            return failure_response("Could not create asset bundle from base64 string!")
        elif not isinstance(asset_bundle, AssetBundle):
            return asset_bundle
        item = Item()
        item.asset_bundle = asset_bundle
        item.owner = request.user
        item.save()
        serializer = ItemDetailSerializer(item)
        return success_response(serializer.data)
