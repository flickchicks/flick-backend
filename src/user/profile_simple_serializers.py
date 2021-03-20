from user.models import Profile

from friendship.models import Friend
from rest_framework import serializers


class ProfileSimpleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    # profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    username = serializers.CharField(source="user.username")
    name = serializers.CharField(source="user.first_name")

    class Meta:
        model = Profile
        fields = ("id", "username", "name", "profile_pic", "profile_pic_url")
        read_only_fields = fields


class ProfileFriendRecommendationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    # profile_pic = AssetBundleDetailSerializer(source="profile_asset_bundle")
    username = serializers.CharField(source="user.username")
    name = serializers.CharField(source="user.first_name")
    num_mutual_friends = serializers.SerializerMethodField(method_name="get_num_mutal_friend")

    def get_num_mutal_friend(self, profile):
        request = self.context.get("request")
        if not request:
            return 0
        user = request.user
        if not Profile.objects.filter(user=user):
            return 0
        request_user_friends = Friend.objects.all().filter(from_user=user).values_list("to_user")
        profile_user_mutual_friends = (
            Friend.objects.all().filter(from_user=profile.user).filter(to_user__in=request_user_friends)
        )
        return profile_user_mutual_friends.count()

    class Meta:
        model = Profile
        fields = ("id", "username", "name", "profile_pic", "profile_pic_url", "num_mutual_friends")
        read_only_fields = fields
