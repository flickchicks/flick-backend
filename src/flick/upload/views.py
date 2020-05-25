from django.conf import settings 

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from api import settings as api_settings
from api.generics import generics

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
            image_data = base64.b64decode(re.sub('^data:image/.+;base64,', '', data['image']))

            # get PIL image
            image = Image.open(BytesIO(image_data))

            image_format = image.format.lower()

            if image_format not in ['jpeg', 'jpg', 'png', 'gif']:
                return Response({'error': 'Image type not accepted. Must be jpeg, jpg, png, or gif.'}, status=status.HTTP_400_BAD_REQUEST)

            salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
            print(salt)

            # save the image as {salt}.png in src/flick/tmp
            image.save(f'tmp/{salt}.{image_format}')

        except Exception as e:
            return Response({'error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

        data = {"test" : "123"}
        return Response(data, status=status.HTTP_200_OK)