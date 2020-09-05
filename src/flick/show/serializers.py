from user.models import Profile

from comment.serializers import CommentSerializer
from django.db.models import Avg
from django.db.models import Q
from friendship.models import Friend
from rest_framework import serializers
from tag.simple_serializers import TagSimpleSerializer

from .models import Show


class ShowSerializer(serializers.ModelSerializer):
    tags = TagSimpleSerializer(read_only=True, many=True)
    comments = serializers.SerializerMethodField(method_name="get_friends_and_user_comments")
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
            "comments",
            "platforms",
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

    def get_friends_and_user_comments(self, instance):
        request = self.context.get("request")
        user = request.user
        if not Profile.objects.filter(user=user):
            return []
        profile = Profile.objects.get(user=user)
        friends = Friend.objects.friends(user=user)
        comments = instance.comments.filter(Q(owner__in=friends) | Q(owner=profile))
        return CommentSerializer(comments, many=True, context={"request": request}).data


class ShowSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = (
            "id",
            "title",
            "poster_pic",
            "is_tv",
            "plot",
            "date_released",
            "status",
            "language",
            "duration",
            "seasons",
            "audience_level",
            "keywords",
        )
        read_only_fields = fields
