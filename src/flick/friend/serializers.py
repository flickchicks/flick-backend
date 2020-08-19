from asset.serializers import AssetBundleDetailSerializer
from django.contrib.auth.models import User
from friendship.models import Friend
from friendship.models import FriendshipRequest
from rest_framework import serializers


class FriendUserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(source="profile.bio")
    profile_pic = AssetBundleDetailSerializer(source="profile.profile_asset_bundle")

    class Meta:
        model = User
        fields = (User.USERNAME_FIELD, "id", "first_name", "last_name", "bio", "profile_pic")
        write_only_fields = fields


class FriendRequestSerializer(serializers.ModelSerializer):

    to_user = FriendUserSerializer(read_only=True)

    class Meta:
        model = FriendshipRequest
        fields = ("to_user", "created", "rejected", "viewed")
        read_only_fields = fields


class IncomingRequestSerializer(serializers.ModelSerializer):

    from_user = FriendUserSerializer(read_only=True)

    class Meta:
        model = FriendshipRequest
        fields = ("from_user", "created", "rejected", "viewed")
        read_only_fields = fields


class FriendshipSerializer(serializers.ModelSerializer):

    from_user = FriendUserSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ("from_user", "created")
        read_only_fields = fields
