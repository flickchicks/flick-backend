from django.contrib.auth.models import User

from rest_framework import serializers


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
