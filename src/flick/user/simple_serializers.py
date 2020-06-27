from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from rest_framework import serializers

from asset.serializers import AssetBundleDetailSerializer
from user.models import Profile
from .serializers import UserSerializer


class ProfileSimpleSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(source="id")
    user_id = serializers.CharField(source="user.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    username = serializers.CharField(source="user.username")
    profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")

    class Meta:
        model = Profile
        fields = ("user_id", "username", "first_name", "last_name", "profile_id", "profile_pic", "bio")
        read_only_fields = fields
