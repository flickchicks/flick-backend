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
    id = serializers.IntegerField(source="user.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    username = serializers.CharField(source="user.username")
    profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    owner_lst = serializers.SerializerMethodField("get_owner_lsts")
    collab_lst = serializers.SerializerMethodField("get_collab_lsts")

    def get_owner_lsts(self, profile):
        lists = profile.owner_lsts.all().filter(is_private=False)
        return LstSerializer(lists, read_only=True, many=True).data

    def get_collab_lsts(self, profile):
        lists = profile.collab_lsts.all().filter(Q(is_private=False) | Q(collaborators=profile))
        return LstSerializer(lists, read_only=True, many=True).data

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_pic",
            "bio",
            "collab_lst",
            "owner_lst",
        )
        read_only_fields = fields
