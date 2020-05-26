from django.conf import settings 

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api import settings as api_settings
from api.generics import generics
from asset.models import Asset, AssetBundle
from asset.serializers import AssetBundleDetailSerializer

import boto3
from PIL import Image
from io import BytesIO
import base64, json, os, random, re, string


# Create your views here.
class UploadImage(generics.CreateAPIView):

    serializer_class = Serializer

    def upload_image(self, request, salt, img, img_format, kind, width, height):
        # secure way of generating a random string        
        img_filename = f'{salt}_{kind}.{img_format}'
        img_temploc = f'{settings.TEMP_DIR}/{img_filename}'
        img.save(img_temploc)

        s3_client = boto3.client('s3')
        s3_client.upload_file(img_temploc, settings.S3_BUCKET, f'image/{img_filename}')
        
        s3_resource = boto3.resource('s3')
        # make s3 image url public
        object_acl = s3_resource.ObjectAcl(settings.S3_BUCKET, f'image/{img_filename}')
        response = object_acl.put(ACL='public-read')

        # create asset bundle
        asset_bundle = AssetBundle()
        asset_bundle.salt = salt
        asset_bundle.kind = 'image'
        asset_bundle.base_url = settings.S3_BASE_URL
        asset_bundle.owner = request.user
        asset_bundle.save()

        # start making asset
        asset = Asset()
        asset.asset_bundle = asset_bundle
        asset.kind = 'original'
        asset.width = img.width
        asset.height = img.height 
        asset.extension = img_format
        asset.save()

        # os.remove(img_temploc)
        return asset_bundle

    # client is expected to send a base64 string
    def post(self, request):
        data = json.loads(request.body)

        if not 'image' in data:
            return Response({'error': 'no image in request.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # remove header of base64 string
            img_data = base64.b64decode(re.sub('^data:image/.+;base64,', '', data['image']))

            # get PIL image
            img = Image.open(BytesIO(img_data))

            img_format = img.format.lower()

            if img_format not in ['jpeg', 'jpg', 'png', 'gif']:
                return Response({'error': 'Image type not accepted. Must be jpeg, jpg, png, or gif.'}, status=status.HTTP_400_BAD_REQUEST)

            asset_bundle = None

            aspect = img.width / img.height 

            salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

            width, height = 0, 0
            for kind, _ in Asset.KIND_CHOICES:
                new_img = img
                if kind is 'original':
                    width = img.width
                    height = img.height
                elif kind is 'large':
                    width = 1024
                    height = int(aspect * 1024)
                    new_img = new_img.resize((width, height))
                elif kind is 'small':
                    width = 128
                    height = int(aspect * 128)
                    new_img = new_img.resize((width, height))
                else: 
                    print(f"error: image {kind} not handled yet!")
                asset_bundle = self.upload_image(request, salt, new_img, img_format, kind, width, height)

        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssetBundleDetailSerializer(asset_bundle)
        return Response(serializer.data, status=status.HTTP_200_OK)