from user.models import Profile

from comment.serializers import CommentSerializer
from django.db.models import Avg
from friendship.models import Friend
from provider.serializers import ProviderSerializer
from rest_framework import serializers
from tag.simple_serializers import TagSimpleSerializer

from .models import Show


class ShowSerializer(serializers.ModelSerializer):
    tags = TagSimpleSerializer(read_only=True, many=True)
    comments = serializers.SerializerMethodField(method_name="get_comments")
    friends_rating = serializers.SerializerMethodField(method_name="calculate_friends_rating")
    user_rating = serializers.SerializerMethodField(method_name="get_user_rating")
    providers = ProviderSerializer(read_only=True, many=True)

    class Meta:
        model = Show
        fields = (
            "id",
            "ext_api_id",
            "ext_api_source",
            "title",
            "poster_pic",
            "backdrop_pic",
            "directors",
            "is_tv",
            "is_adult",
            "date_released",
            "providers",
            "status",
            "language",
            "duration",
            "plot",
            "tags",
            "seasons",
            "imdb_rating",
            "tomato_rating",
            "friends_rating",
            "user_rating",
            "comments",
            "keywords",
            "cast",
        )
        read_only_fields = fields

    def calculate_friends_rating(self, instance):
        request = self.context.get("request")
        user = request.user
        friends = Friend.objects.friends(user=user)
        ratings = instance.ratings.filter(rater__in=friends).aggregate(Avg("score")).get("score__avg")
        return ratings

    def get_user_rating(self, instance):
        request = self.context.get("request")
        user = request.user
        if not instance.ratings.filter(rater=user):
            return None
        return instance.ratings.get(rater=user).score

    def get_comments(self, instance):
        request = self.context.get("request")
        user = request.user
        if not Profile.objects.filter(user=user):
            return []
        return CommentSerializer(instance.comments, many=True, context={"request": request}).data


class ShowSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = (
            "id",
            "ext_api_id",
            "ext_api_source",
            "title",
            "poster_pic",
            "backdrop_pic",
            "is_tv",
            "is_adult",
            "plot",
            "date_released",
            "language",
        )
        read_only_fields = fields
