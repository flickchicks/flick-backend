import json

from api.generics import generics
from api.utils import failure_response
from api.utils import success_response
from asset.serializers import AssetBundleDetailSerializer

from .utils import upload_image_helper


class UploadImage(generics.CreateAPIView):

    serializer_class = AssetBundleDetailSerializer

    def post(self, request):
        data = json.loads(request.body)
        if "image" not in data:
            return failure_response("No image in request.")
        image_data = data["image"]
        img_url = upload_image_helper(image_data)
        return success_response(img_url)
