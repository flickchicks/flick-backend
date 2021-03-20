from mimetypes import guess_extension
from mimetypes import guess_type
import random
import string

from api.utils import failure_response
from django.conf import settings

from .tasks import async_upload_image


def upload_image_helper(image_data):
    img_ext = guess_extension(guess_type(image_data)[0])[1:]
    if img_ext not in ["jpeg", "jpg", "png", "gif"]:
        return failure_response("Image type not accepted. Must be jpeg, jpg, png, or gif.")
    salt = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
    img_filename = f"{salt}.{img_ext}"
    async_upload_image.delay(image_data, img_filename)
    img_url = f"{settings.S3_BASE_URL}image/{img_filename}"
    return img_url
