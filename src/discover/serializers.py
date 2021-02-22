from random import sample
from user.profile_simple_serializers import ProfileSimpleSerializer

from comment.serializers import SimpleCommentSerializer
from discover_recommend.serializers import DiscoverRecommendationSerializer
from lst.serializers import LstWithSimpleShowsSerializer
from rest_framework import serializers

from .models import Discover


class DiscoverSerializer(serializers.ModelSerializer):
    friend_recommendations = ProfileSimpleSerializer(many=True)
    list_recommendations = LstWithSimpleShowsSerializer(many=True)
    show_recommendations = serializers.SerializerMethodField(method_name="select_show_rec")
    friend_comments = SimpleCommentSerializer(many=True)

    class Meta:
        model = Discover
        fields = ("friend_recommendations", "list_recommendations", "show_recommendations", "friend_comments")
        ready_only_fields = fields

    def select_show_rec(self, instance):
        # request = self.context.get("request")
        # user = request.user

        # profile = Profile.objects.get(user=user)
        shows = list(instance.show_recommendations.all())
        select_shows = sample(shows, 10)
        select_shows_data = [DiscoverRecommendationSerializer(show).data for show in select_shows]
        print(select_shows_data)
        return select_shows_data
