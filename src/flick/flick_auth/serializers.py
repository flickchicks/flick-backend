from django.contrib.auth.models import User
from rest_framework import serializers


class AuthenticateSerializer(serializers.ModelSerializer):
    profile_pic = serializers.CharField(source="profile.profile_pic")
    social_id = serializers.CharField(source="profile.social_id")
    social_id_token = serializers.CharField(source="profile.social_id_token")
    social_id_token_type = serializers.CharField(source="profile.social_id_token_type")
    auth_token = serializers.SerializerMethodField(method_name="get_auth_token")

    class Meta:
        model = User
        fields = (
            "auth_token",
            User.USERNAME_FIELD,
            "first_name",
            "last_name",
            "profile_pic",
            "social_id",
            "social_id_token",
            "social_id_token_type",
            "date_joined",
        )
        write_only_fields = fields

    def get_auth_token(self, instance):
        return self.context.get("auth_token")


class RegisterSerializer(serializers.ModelSerializer):
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


class LogoutSerializer(serializers.Serializer):
    pass
