from user.models import Profile

from asset.serializers import AssetBundleDetailSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from lst.serializers import LstSerializer
from lst.simple_serializers import MeLstSerializer
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
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
    id = serializers.IntegerField(source="user.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    username = serializers.CharField(source="user.username")
    profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    owner_lsts = MeLstSerializer(many=True)
    collab_lsts = MeLstSerializer(many=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_pic",
            "bio",
            "phone_number",
            "social_id_token_type",
            "social_id_token",
            "num_notifs",
            "owner_lsts",
            "collab_lsts",
        )
        read_only_fields = fields


class FriendProfileSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(source="id")
    user_id = serializers.CharField(source="user.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    username = serializers.CharField(source="user.username")
    profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    public_owner_lst = serializers.SerializerMethodField("public_owner_lsts")
    public_collab_lst = serializers.SerializerMethodField("public_collab_lsts")

    def public_owner_lsts(self, profile):
        lists = profile.owner_lsts.all().filter(is_private=False)
        serializer = LstSerializer(lists, read_only=True, many=True)
        return serializer.data

    def public_collab_lsts(self, profile):
        lists = profile.collab_lsts.all().filter(Q(is_private=False) | Q(collaborators=profile))
        serializer = LstSerializer(lists, read_only=True, many=True)
        return serializer.data

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
            "public_collab_lst",
            "public_owner_lst",
        )
        read_only_fields = fields
