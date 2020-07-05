from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from .utils import AuthTools
from asset.serializers import AssetBundleDetailSerializer
from user.models import Profile
from user.serializers import ProfileSerializer, UserSerializer


class ProfileRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("profile_pic", "social_id_token", "social_id_token_type")
        write_only_fields = ("profile_pic", "social_id_token", "social_id_token_type")


class UserRegisterSerializer(serializers.ModelSerializer):
    profile_pic = serializers.CharField(source="profile.profile_pic")
    social_id_token = serializers.CharField(source="profile.social_id_token")
    social_id_token_type = serializers.CharField(source="profile.social_id_token_type")

    class Meta:
        model = User
        fields = (
            User.USERNAME_FIELD,
            "first_name",
            "last_name",
            "profile_pic",
            "social_id_token",
            "social_id_token_type",
        )
        write_only_fields = fields


class LoginSerializer(serializers.Serializer):
    auth_token = serializers.CharField(source="key", read_only=True)
    username = serializers.CharField()
    social_id_token = serializers.CharField()


class LoginCompleteSerializer(serializers.Serializer):
    auth_token = serializers.CharField(source="key", read_only=True)


class LogoutSerializer(serializers.Serializer):
    pass
