import json

from api.generics import generics
from api.utils import failure_response
from api.utils import success_response
from asset.models import AssetBundle
from asset.serializers import AssetBundleDetailSerializer

from .utils import upload_image


class UploadImage(generics.CreateAPIView):

    serializer_class = AssetBundleDetailSerializer

    def post(self, request):
        data = json.loads(request.body)
        if "image" not in data:
            return failure_response("No image in request.")
        asset_bundle = upload_image(data["image"], request.user)
        if not asset_bundle or not isinstance(asset_bundle, AssetBundle):
            return failure_response("Could not create asset bundle from base64 string!")
        return success_response(self.serializer_class(asset_bundle).data)
