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


class UploadImage(generics.CreateAPIView):

    serializer_class = Serializer

    def post(self, request):
        data = json.loads(request.body)

        if "image" not in data:
            return Response(
                {"error": "no image in request."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # [1:] strips off leading period
            img_ext = guess_extension(guess_type(data["image"])[0])[1:]

            if img_ext not in ["jpeg", "jpg", "png", "gif"]:
                return Response(
                    {
                        "error": "Image type not accepted. Must be jpeg, jpg, png, or gif."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # remove header of base64 string
            img_str = re.sub("^data:image/.+;base64,", "", data["image"])

            # secure way of generating random string for image name
            salt = "".join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                for _ in range(16)
            )

            asset_bundle = AssetBundle()
            asset_bundle.salt = salt
            asset_bundle.kind = "image"
            asset_bundle.base_url = settings.S3_BASE_URL
            asset_bundle.owner = request.user
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

            item = Item()
            item.asset_bundle = asset_bundle
            item.owner = request.user
            item.save()

        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ItemDetailSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
