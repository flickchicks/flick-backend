import json

from api.generics import generics
from api.utils import failure_response
from api.utils import success_response
from asset.models import AssetBundle
from item.models import Item
from item.serializers import ItemDetailSerializer
from rest_framework.serializers import Serializer

from .utils import upload_image


class UploadImage(generics.CreateAPIView):

    serializer_class = Serializer

    def post(self, request):
        data = json.loads(request.body)
        if "image" not in data:
            return failure_response("No image in request.")
        asset_bundle = upload_image(data["image"], request.user)
        if not asset_bundle:
            return failure_response("Could not create asset bundle from base64 string!")
        elif not isinstance(asset_bundle, AssetBundle):
            return asset_bundle
        item = Item()
        item.asset_bundle = asset_bundle
        item.owner = request.user
        item.save()
        serializer = ItemDetailSerializer(item)
        return success_response(serializer.data)
