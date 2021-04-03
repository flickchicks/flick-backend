from user.models import Profile
from user.profile_simple_serializers import ProfileFriendRecommendationSerializer

from comment.serializers import CommentDiscoverSerializer
from django.db.models import Prefetch
from friendship.models import Friend
from lst.models import LstSaveActivity
from lst.serializers import LstDiscoverSerializer
from lst.serializers import LstSaveActivitySerializer
from rest_framework import serializers
from show.simple_serializers import ShowSimpleSerializer

from .models import Discover


class DiscoverSerializer(serializers.ModelSerializer):
    friend_recommendations = serializers.SerializerMethodField(method_name="get_friend_recommendations")
    friend_lsts = serializers.SerializerMethodField(method_name="select_friend_lsts")
    friend_shows = serializers.SerializerMethodField(method_name="select_friend_shows")
    friend_comments = serializers.SerializerMethodField(method_name="select_friend_comments")

    class Meta:
        model = Discover
        fields = (
            "friend_recommendations",
            "friend_lsts",
            "friend_shows",
            "friend_comments",
        )
        ready_only_fields = fields

    def select_friend_comments(self, instance):
        comments = instance.friend_comments.order_by("-created_at")
        serializer = CommentDiscoverSerializer(comments, many=True)
        return serializer.data

    def select_friend_lsts(self, instance):
        serializer = LstDiscoverSerializer(instance.friend_lsts, many=True, context=self.context)
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

        queryset = LstSaveActivity.objects.filter(saved_by__in=friends).prefetch_related("saved_by", "lst")
        friend_shows = instance.friend_shows.all().prefetch_related(
            Prefetch("activity", queryset=queryset, to_attr="show_activities",)
        )

        data = []

        for show in friend_shows:
            serializer_data = ShowSimpleSerializer(show, many=False).data
            serializer_data["saved_to_lsts"] = LstSaveActivitySerializer(show.show_activities, many=True).data
            data.append(serializer_data)
        return data
