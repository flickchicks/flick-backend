from asset.serializers import AssetBundleDetailSerializer
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSimpleSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(source="profile.id")
    user_id = serializers.IntegerField(source="id")
    profile_pic = AssetBundleDetailSerializer(source="profile.profile_asset_bundle")

    class Meta:
        model = User
        fields = ("user_id", "username", "first_name", "last_name", "profile_id", "profile_pic")
        read_only_fields = fields
