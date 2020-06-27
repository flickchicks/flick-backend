from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from friendship.models import Friend, Follow, Block
from rest_framework import serializers

from asset.serializers import AssetBundleDetailSerializer
from lst.simple_serializers import LstSimpleSerializer
from user.models import Profile


class UserSerializer(serializers.ModelSerializer):

    # profile = ProfileSerializer(many=False)

    groups = serializers.SerializerMethodField("get_user_groups")

    def get_user_groups(self, user):
        results = []
        for group in user.groups.all():
            results.append(group.name)
        return results

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "first_name", "last_name", "groups")
        read_only_fields = fields


class UserDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "first_name", "last_name", "email", "groups")
        read_only_fields = fields


class UserListSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "first_name", "last_name", "email")
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(source="id")
    user_id = serializers.CharField(source="user.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    username = serializers.CharField(source="user.username")
    profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    owner_lsts = LstSimpleSerializer(many=True)
    collab_lsts = LstSimpleSerializer(many=True)

    class Meta:
        model = Profile
        fields = (
            "user_id",
            "username",
            "first_name",
            "last_name",
            "profile_id",
            "profile_pic",
            "bio",
            "phone_number",
            "social_id_token_type",
            "social_id_token",
            "owner_lsts",
            "collab_lsts",
        )
        read_only_fields = fields
