from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from rest_framework import serializers

from .serializers import UserSerializer
from asset.serializers import AssetBundleDetailSerializer
from user.models import Profile


class UserSimpleSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(source="profile.id")
    user_id = serializers.CharField(source="id")
    profile_pic = AssetBundleDetailSerializer(source="profile.profile_asset_bundle")

    class Meta:
        model = User
        fields = ("user_id", "username", "first_name", "last_name", "profile_id", "profile_pic")
        read_only_fields = fields
