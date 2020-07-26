from django.db.models import Avg
from friendship.models import Friend
from rest_framework import serializers
from tag.simple_serializers import TagSimpleSerializer

from .models import Show


class ShowSerializer(serializers.ModelSerializer):
    tags = TagSimpleSerializer(read_only=True, many=True)
    friends_rating = serializers.SerializerMethodField(method_name="calculate_friends_rating")
    user_rating = serializers.SerializerMethodField(method_name="get_user_rating")

    class Meta:
        model = Show
        fields = (
            "id",
            "title",
            "poster_pic",
            "directors",
            "is_tv",
            "date_released",
            "status",
            "language",
            "duration",
            "plot",
            "tags",
            "seasons",
            "audience_level",
            "imdb_rating",
            "tomato_rating",
            "friends_rating",
            "user_rating",
            "platforms",
            "keywords",
            "cast",
        )
        read_only_fields = ("id",)

    def calculate_friends_rating(self, instance):
        request = self.context.get("request")
        user = request.user
        # TODO: check if user is authenticated
        friends = Friend.objects.friends(user=user)
        ratings = instance.ratings.filter(rater__in=friends).aggregate(Avg("score")).get("score_avg")
        return ratings

    def get_user_rating(self, instance):
        request = self.context.get("request")
        user = request.user
        if not instance.ratings.filter(rater=user):
            return None
        return instance.ratings.get(rater=user).score
