from django.conf import settings 

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api import settings as api_settings
from api.generics import generics

from PIL import Image
from io import BytesIO
import base64, json, re


# Create your views here.
class UploadImage(generics.CreateAPIView):

    serializer_class = Serializer

    # client is expected to send a base64 string
    def post(self, request):
        print(f"{request.user}")
        data = json.loads(request.body)

        if not 'image' in data:
            return Response({'error': 'no image in request.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            image_data = base64.b64decode(re.sub('^data:image/.+;base64,', '', data['image']))

            image = Image.open(BytesIO(image_data))

            if image.format.lower() not in ['jpeg', 'jpg', 'png', 'gif']:
                return Response({'error': 'Image type not accepted. Must be jpeg, jpg, png, or gif.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

        data = {"test" : "123"}
        return Response(data, status=status.HTTP_200_OK)