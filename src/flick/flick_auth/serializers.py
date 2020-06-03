from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

from asset.serializers import AssetBundleDetailSerializer
from user.serializers import ProfileSerializer, UserSerializer
from .utils import AuthTools
from user.models import Profile

User = get_user_model()


class ProfileRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("profile_pic", "social_id_token", "social_id_token_type")
        write_only_fields = ("profile_pic", "social_id_token", "social_id_token_type")


class UserRegisterSerializer(serializers.ModelSerializer):

    profile = ProfileRegisterSerializer()

    class Meta:
        model = User
        # Django's REQUIRED_FIELDS tuple(User.REQUIRED_FIELDS) +
        fields = (User.USERNAME_FIELD, "first_name", "last_name", "profile")
        write_only_fields = ("first_name", "last_name", "profile")

    def save(self, **kwargs):
        data = self.init_data if hasattr(self, "init_data") else self.initial_data

        items = dict(data.items())
        user_data = {
            "username": items["username"],
            "first_name": items["first_name"],
            "last_name": items["last_name"],
            "password": items["profile.social_id_token"],
        }

        profile_data = {
            "profile_pic": items["profile.profile_pic"],
            "social_id_token": items["profile.social_id_token"],
            "social_id_token_type": items["profile.social_id_token_type"],
            "role": "consumer",
        }

        group = profile_data["role"] + "_basic"
        user = AuthTools.register(user_data, profile_data, group)

        if user is not None:
            self.object = user
            return self.object

        raise serializers.ValidationError("Unable to register with the credentials provided.")


class LoginSerializer(serializers.Serializer):
    auth_token = serializers.CharField(source="key", read_only=True)
    # user = UserSerializer(many=False, read_only=True)

    username = serializers.CharField()
    social_id_token = serializers.CharField()

    # class Meta:
    #     model = Token
    #     fields = (
    #         'auth_token',
    #         'user',
    #         'password'
    #     )
    #     read_only_fields = fields


class LoginCompleteSerializer(serializers.Serializer):

    auth_token = serializers.CharField(source="key", read_only=True)


class LogoutSerializer(serializers.Serializer):
    pass
