import base64
import json
import os
import random
import re
import string
from io import BytesIO
from mimetypes import guess_extension, guess_type

import boto3
from api import settings as api_settings
from api.generics import generics
from asset.models import Asset, AssetBundle
from django.conf import settings
from flick.tasks import add, resize_and_upload
from item.models import Item
from item.serializers import ItemDetailSerializer
from PIL import Image
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from .utils import upload_image


class UploadImage(generics.CreateAPIView):

    serializer_class = Serializer

    def post(self, request):
        asset_bundle = upload_image(request)
        if not asset_bundle:
            return Response(
                {"Error": "Could not create asset bundle from base64 string!"}, status=status.HTTP_400_BAD_REQUEST
            )
        item = Item()
        item.asset_bundle = asset_bundle
        item.owner = request.user
        item.save()
        serializer = ItemDetailSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
