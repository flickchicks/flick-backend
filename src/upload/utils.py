from mimetypes import guess_extension
from mimetypes import guess_type
import random
import re
import string

from api.utils import failure_response
from django.conf import settings
from flick.tasks import async_upload_image
from rest_framework import status


def upload_image(image_data, user):
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
        img_filename = f"{salt}.{img_ext}"
        print("img_filename", img_filename)
        async_upload_image.delay(salt, img_str, img_ext)
        return f"{settings.S3_BASE_URL}image/{img_filename}"
    except Exception as e:
        return failure_response(f"Unable to upload image because of {e}.")
    return failure_response("Image upload no longer supported.")
