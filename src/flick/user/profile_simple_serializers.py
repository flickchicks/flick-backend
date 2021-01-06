from user.models import Profile

from asset.serializers import AssetBundleDetailSerializer
from rest_framework import serializers


class ProfileSimpleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    username = serializers.CharField(source="user.username")
    name = serializers.CharField(source="user.first_name")

    class Meta:
        model = Profile
        fields = ("id", "username", "name", "profile_pic")
        read_only_fields = fields
