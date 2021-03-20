import base64
from io import BytesIO
import json
from mimetypes import guess_extension
from mimetypes import guess_type
import random
import re
import string

from api.generics import generics
from api.utils import failure_response
from api.utils import success_response
from asset.serializers import AssetBundleDetailSerializer
import boto3
from django.conf import settings
from PIL import Image


class UploadImage(generics.CreateAPIView):

    serializer_class = AssetBundleDetailSerializer

    def post(self, request):
        data = json.loads(request.body)
        if "image" not in data:
            return failure_response("No image in request.")
        img_url = "hi"
        # img_url = upload_image(data["image"], request.user)
        image_data = data["image"]
        img_ext = guess_extension(guess_type(image_data)[0])[1:]

        if img_ext not in ["jpeg", "jpg", "png", "gif"]:
            return failure_response("Image type not accepted. Must be jpeg, jpg, png, or gif.")

        # remove header of base64 string
        img_str = re.sub("^data:image/.+;base64,", "", image_data)
        # secure way of generating random string for image name
        salt = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        img_filename = f"{salt}.{img_ext}"
        img_data = base64.b64decode(img_str)
        # print("img_data", img_data)
        img = Image.open(BytesIO(img_data))
        img_filename = f"{salt}.{img_ext}"
        img_temploc = "tmp/" + img_filename  # f"{os.getcwd()}{settings.TEMP_DIR}/{img_filename}"
        print("img_temploc", img_temploc)
        img.save(img_temploc)

        s3_client = boto3.client("s3")
        print("s3", s3_client)
        res = s3_client.upload_file(img_temploc, settings.S3_BUCKET, f"image/{img_filename}")
        print("res", res)
        # # make S3 image url public
        s3_resource = boto3.resource("s3")
        object_acl = s3_resource.ObjectAcl(settings.S3_BUCKET, f"image/{img_filename}")
        object_acl.put(ACL="public-read")

        img_url = f"{settings.S3_BASE_URL}image/{img_filename}"
        # print("img_url", img_url)
        # if img_url is None or type(img_url) != str:
        #     return img_url
        return success_response(img_url)
