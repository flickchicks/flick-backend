from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField
from user.models import Profile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "bio", "profile_pic", "phone_number", "social_id_token_type", "social_id_token")
        read_only_fields = ("id",)


class UserSerializer(ModelSerializer):
    """
    User Serializer
    """

    profile = ProfileSerializer(many=False)

    groups = SerializerMethodField("get_user_groups")

    def get_user_groups(self, user):
        results = []
        for group in user.groups.all():
            results.append(group.name)

        return results

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "first_name", "last_name", "email", "profile", "groups")
        read_only_fields = ("id", "groups", "profile")


class UserDetailSerializer(UserSerializer):
    """
    User Detail Serializer
    """

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "first_name", "last_name", "email", "groups")
        read_only_fields = fields


class UserListSerializer(UserSerializer):
    """
    User List Serializer
    """

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "first_name", "last_name", "email")
        read_only_fields = fields
