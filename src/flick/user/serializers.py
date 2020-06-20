from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from friendship.models import Friend, Follow, Block
from rest_framework import serializers

from asset.serializers import AssetBundleDetailSerializer
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
    profile_asset_bundle = AssetBundleDetailSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "bio",
            "profile_asset_bundle",
            "phone_number",
            "social_id_token_type",
            "social_id_token",
            # "owner_lsts",
            # "collab_lsts",
        )
        read_only_fields = fields
