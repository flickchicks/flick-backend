from random import sample
from user.profile_simple_serializers import ProfileFriendRecommendationSerializer

from comment.serializers import SimpleCommentSerializer
from discover_recommend.serializers import DiscoverRecommendationSerializer
from rest_framework import serializers

from .models import Discover


class DiscoverSerializer(serializers.ModelSerializer):
    friend_recommendations = serializers.SerializerMethodField(method_name="get_friend_recommendations")
    show_recommendations = serializers.SerializerMethodField(method_name="select_show_rec")
    list_recommendations = serializers.SerializerMethodField(method_name="select_lst_rec")
    friend_comments = SimpleCommentSerializer(many=True)

    class Meta:
        model = Discover
        fields = ("friend_recommendations", "list_recommendations", "show_recommendations", "friend_comments")
        ready_only_fields = fields

    def get_friend_recommendations(self, instance):
        return ProfileFriendRecommendationSerializer(
            instance.friend_recommendations, many=True, context=self.context
        ).data

    def select_show_rec(self, instance):
        shows = list(instance.show_recommendations.all())
        select_shows = sample(shows, min(10, len(shows)))
        serializer = DiscoverRecommendationSerializer(select_shows, many=True)
        return serializer.data

    def select_lst_rec(self, instance):
        lsts = list(instance.list_recommendations.all())
        select_lsts = sample(lsts, min(10, len(lsts)))
        serializer = DiscoverRecommendationSerializer(select_lsts, many=True)
        return serializer.data
