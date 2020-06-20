from django.contrib.auth.models import User

from friendship.models import Friend, Follow, Block, FriendshipRequest
from rest_framework import serializers

from asset.serializers import AssetBundleDetailSerializer
from user.models import Profile


class FriendProfileSerializer(serializers.ModelSerializer):

    profile_asset_bundle = AssetBundleDetailSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ("bio", "profile_asset_bundle", "owner_lsts", "collab_lsts")
        read_only_fields = ("id",)


class FriendUserSerializer(serializers.ModelSerializer):
    """
    User Serializer
    """

    profile = FriendProfileSerializer(many=False)

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "first_name", "last_name", "profile")
        read_only_fields = fields


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Friend Request Serializer
    """

    to_user = FriendUserSerializer(read_only=True)

    class Meta:
        model = FriendshipRequest
        fields = ("to_user", "created", "rejected", "viewed")
        read_only_fields = fields


class IncomingRequestSerializer(serializers.ModelSerializer):
    """
    Friend Request Serializer
    """

    from_user = FriendUserSerializer(read_only=True)

    class Meta:
        model = FriendshipRequest
        fields = ("from_user", "created", "rejected", "viewed")
        read_only_fields = fields


class FriendshipSerializer(serializers.ModelSerializer):
    """
    Friend Serializer
    """

    to_user = FriendUserSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ("to_user", "created")
        read_only_fields = fields
