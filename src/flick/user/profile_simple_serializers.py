from user.models import Profile

from asset.serializers import AssetBundleDetailSerializer
from rest_framework import serializers


class ProfileSimpleSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(source="id")
    user_id = serializers.CharField(source="user.id")
    profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Profile
        fields = ("user_id", "username", "first_name", "last_name", "profile_id", "profile_pic")
        read_only_fields = fields


class ProfileSimplestSerializer(serializers.ModelSerializer):
    profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")

    class Meta:
        model = Profile
        fields = ("profile_pic",)
        read_only_fields = fields
