import json
from mimetypes import guess_extension
from mimetypes import guess_type
import random
import string

from api.generics import generics
from api.utils import failure_response
from api.utils import success_response
from asset.serializers import AssetBundleDetailSerializer
from django.conf import settings

from .tasks import upload_image


class UploadImage(generics.CreateAPIView):

    serializer_class = AssetBundleDetailSerializer

    def post(self, request):
        data = json.loads(request.body)
        if "image" not in data:
            return failure_response("No image in request.")
        img_url = "hi"
        image_data = data["image"]
        img_ext = guess_extension(guess_type(image_data)[0])[1:]

        if img_ext not in ["jpeg", "jpg", "png", "gif"]:
            return failure_response("Image type not accepted. Must be jpeg, jpg, png, or gif.")

        # remove header of base64 string
        # secure way of generating random string for image name
        salt = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

        img_filename = f"{salt}.{img_ext}"

        upload_image.delay(image_data, img_filename)

        img_url = f"{settings.S3_BASE_URL}image/{img_filename}"
        return success_response(img_url)
