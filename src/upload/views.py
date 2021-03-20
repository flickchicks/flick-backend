import json

from api.generics import generics
from api.utils import failure_response
from api.utils import success_response
from asset.serializers import AssetBundleDetailSerializer

from .utils import upload_image


class UploadImage(generics.CreateAPIView):

    serializer_class = AssetBundleDetailSerializer

    def post(self, request):
        data = json.loads(request.body)
        if "image" not in data:
            return failure_response("No image in request.")
        img_url = upload_image(data["image"], request.user)
        print("img_url", img_url)
        if img_url is None or type(img_url) != str:
            return img_url
        return success_response(img_url)
