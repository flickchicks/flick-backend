from user.models import Profile

from django.contrib.auth.models import User
from django.db.models import Q
from friendship.models import Friend
from lst.simple_serializers import MeLstSerializer
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField("get_user_groups")
    name = serializers.CharField(source="first_name")

    def get_user_groups(self, user):
        results = []
        for group in user.groups.all():
            results.append(group.name)
        return results

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "name", "groups")
        read_only_fields = fields


class UserDetailSerializer(UserSerializer):
    name = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "name", "email", "groups")
        read_only_fields = fields


class UserListSerializer(UserSerializer):
    name = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "name", "email")
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    name = serializers.CharField(source="user.first_name")
    username = serializers.CharField(source="user.username")
    # profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    owner_lsts = MeLstSerializer(many=True)
    collab_lsts = MeLstSerializer(many=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "name",
            "profile_pic",
            "bio",
            "phone_number",
            "social_id",
            "social_id_token_type",
            "social_id_token",
            "num_notifs",
            "owner_lsts",
            "collab_lsts",
        )
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    friend_status = serializers.SerializerMethodField("get_friend_status")
    name = serializers.CharField(source="user.first_name")
    username = serializers.CharField(source="user.username")
    # profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    owner_lsts = serializers.SerializerMethodField("get_owner_lsts")
    collab_lsts = serializers.SerializerMethodField("get_collab_lsts")

    def get_owner_lsts(self, profile):
        lists = profile.owner_lsts.all().filter(is_private=False)
        return MeLstSerializer(lists, read_only=True, many=True).data

    def get_collab_lsts(self, profile):
        lists = profile.collab_lsts.all().filter(Q(is_private=False) | Q(collaborators=profile))
        return MeLstSerializer(lists, read_only=True, many=True).data

    def get_friend_status(self, profile):
        other_user = profile.user
        request = self.context.get("request")
        for sent_request in Friend.objects.sent_requests(user=request.user):
            if sent_request.to_user.id == profile.user.id:
                return "outgoing request"
        for sent_request in Friend.objects.sent_requests(user=other_user):
            if sent_request.to_user.id == request.user.id:
                return "incoming request"
        if Friend.objects.are_friends(request.user, other_user):
            return "friends"
        return "not friends"

    class Meta:
        model = Profile
        fields = (
            "id",
            "friend_status",
            "username",
            "name",
            "profile_pic",
            "bio",
            "collab_lsts",
            "owner_lsts",
        )
        read_only_fields = fields
