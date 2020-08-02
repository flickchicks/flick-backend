from rest_framework.serializers import CurrentUserDefault
from rest_framework.serializers import ModelSerializer

from .models import AssetBundle


class AssetBundleSerializer(ModelSerializer):
    class Meta:
        model = AssetBundle
        fields = ("id", "salt", "kind", "base_url", "asset_urls", "created_at")
        read_only_fields = fields

    def save(self):
        self.user = CurrentUserDefault()


class AssetBundleDetailSerializer(ModelSerializer):
    class Meta:
        model = AssetBundle
        fields = ("id", "salt", "kind", "base_url", "asset_urls", "created_at", "updated_at")
        read_only_fields = fields
