from django.contrib.auth.models import User
from rest_framework import serializers


class AuthenticateSerializer(serializers.ModelSerializer):
    profile_pic = serializers.CharField(source="profile.profile_pic")
    profile_pic_url = serializers.CharField(source="profile.profile_pic_url")
    social_id = serializers.CharField(source="profile.social_id")
    social_id_token = serializers.CharField(source="profile.social_id_token")
    social_id_token_type = serializers.CharField(source="profile.social_id_token_type")
    auth_token = serializers.SerializerMethodField(method_name="get_auth_token")
    name = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = (
            "auth_token",
            User.USERNAME_FIELD,
            "name",
            "profile_pic",
            "profile_pic_url",
            "social_id",
            "social_id_token",
            "social_id_token_type",
            "date_joined",
        )
        read_only_fields = fields

    def get_auth_token(self, instance):
        return self.context.get("auth_token")


class LogoutSerializer(serializers.Serializer):
    pass
