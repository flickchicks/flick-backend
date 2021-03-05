from user.models import Profile
from user.profile_simple_serializers import ProfileFriendRecommendationSerializer

from comment.serializers import SimpleCommentSerializer
from friendship.models import Friend
from lst.serializers import LstSaveActivitySerializer
from lst.serializers import LstWithSimpleShowsSerializer
from rest_framework import serializers
from show.simple_serializers import ShowSimpleSerializer

from .models import Discover


class DiscoverSerializer(serializers.ModelSerializer):
    friend_recommendations = serializers.SerializerMethodField(method_name="get_friend_recommendations")
    friend_lsts = serializers.SerializerMethodField(method_name="select_friend_lsts")
    friend_shows = serializers.SerializerMethodField(method_name="select_friend_shows")
    friend_comments = SimpleCommentSerializer(many=True)

    class Meta:
        model = Discover
        fields = (
            "friend_recommendations",
            "friend_lsts",
            "friend_shows",
            "friend_comments",
        )
        ready_only_fields = fields

    def select_friend_lsts(self, instance):
        serializer = LstWithSimpleShowsSerializer(instance.friend_lsts, many=True, context=self.context)
        return serializer.data

    def get_friend_recommendations(self, instance):
        serializer = ProfileFriendRecommendationSerializer(
            instance.friend_recommendations, many=True, context=self.context
        )
        return serializer.data

    def select_friend_shows(self, instance):
        request = self.context.get("request")
        user = request.user
        friends = [Profile.objects.get(user=friend) for friend in Friend.objects.friends(user=user)]
        friend_shows = []

        for show in instance.friend_shows.all():
            serializer_data = ShowSimpleSerializer(show, many=False).data
            activities = show.activity.filter(saved_by__in=friends)
            serializer_data["saved_to_lsts"] = LstSaveActivitySerializer(activities, many=True).data
            friend_shows.append(serializer_data)
        return friend_shows
