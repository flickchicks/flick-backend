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
import base64, json, random, re, string


# Create your views here.
class UploadImage(generics.CreateAPIView):

    serializer_class = Serializer

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

            # secure way of generating a random string
            salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
            
            img_filename = f'{salt}_original.{img_format}'
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
            

        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssetBundleDetailSerializer(asset_bundle)
        return Response(serializer.data, status=status.HTTP_200_OK)