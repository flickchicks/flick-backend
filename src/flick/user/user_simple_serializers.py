from asset.serializers import AssetBundleDetailSerializer
from django.contrib.auth.models import User
from friendship.models import Friend
from rest_framework import serializers


class UserSimpleSerializer(serializers.ModelSerializer):
    profile_pic = AssetBundleDetailSerializer(source="profile.profile_asset_bundle")
    num_mutual_friends = serializers.SerializerMethodField(method_name="get_num_mutual_friends")

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "profile_pic", "num_mutual_friends")
        read_only_fields = fields

    def get_num_mutual_friends(self, instance):
        if not self.context:
            return None
        request = self.context.get("request")
        request_user_friends = Friend.objects.friends(request.user)
        searched_user_friends = Friend.objects.friends(instance)
        mutual_friends = list(set(request_user_friends) & set(searched_user_friends))
        return len(mutual_friends)
