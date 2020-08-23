from api import settings as api_settings
from api.utils import success_response
from rest_framework import generics

from .models import AssetBundle
from .serializers import AssetBundleDetailSerializer
from .serializers import AssetBundleSerializer


class AssetBundleList(generics.ListCreateAPIView):

    queryset = AssetBundle.objects.all()
    serializer_class = AssetBundleSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    # don't need this, generics has this code, but this overrides
    # gives option to add additional checks / customize
    def list(self, request):
        self.serializer_class = AssetBundleSerializer
        return super(AssetBundleList, self).list(request)


class AssetBundleDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = AssetBundle.objects.all()
    serializer_class = AssetBundleDetailSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def retrieve(self, request, pk):
        return success_response(self.serializer_class(self.get_object(), many=False).data)
