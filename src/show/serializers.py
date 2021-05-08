from user.models import Profile

from comment.serializers import CommentSerializer
from django.conf import settings
from django.db.models import Avg
from friendship.models import Friend
from group.models import Group
from provider.serializers import ProviderSerializer
from rest_framework import serializers
from tag.simple_serializers import TagSimpleSerializer
from vote.models import VoteType

from .models import Show


class ShowSerializer(serializers.ModelSerializer):
    tags = TagSimpleSerializer(read_only=True, many=True)
    comments = serializers.SerializerMethodField(method_name="get_comments")
    friends_rating = serializers.SerializerMethodField(method_name="calculate_friends_rating")
    user_rating = serializers.SerializerMethodField(method_name="get_user_rating")
    providers = ProviderSerializer(read_only=True, many=True)
    trailers = serializers.SerializerMethodField(method_name="get_trailer_links")
    images = serializers.SerializerMethodField(method_name="get_image_urls")

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
            "episodes",
            "animelist_rating",
            "animelist_rank",
            "imdb_rating",
            "tomato_rating",
            "friends_rating",
            "user_rating",
            "comments",
            "keywords",
            "cast",
            "trailers",
            "images",
        )
        read_only_fields = fields

    def get_trailer_links(self, instance):
        if not instance.trailer_keys:
            return []
        keys = instance.trailer_keys.split(",")
        return [f"https://www.youtube.com/watch?v={k}" for k in keys]

    def get_image_urls(self, instance):
        if not instance.image_keys:
            return []
        keys = instance.image_keys.split(",")
        return [f"{settings.TMDB_BASE_IMAGE_URL}{k}" for k in keys]

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


class GroupShowSerializer(serializers.ModelSerializer):
    num_yes_votes = serializers.SerializerMethodField(method_name="get_num_yes_votes")
    num_maybe_votes = serializers.SerializerMethodField(method_name="get_num_maybe_votes")
    num_no_votes = serializers.SerializerMethodField(method_name="get_num_no_votes")

    class Meta:
        model = Show
        fields = (
            "id",
            "num_yes_votes",
            "num_maybe_votes",
            "num_no_votes",
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

    def get_num_yes_votes(self, show):
        group_id = self.context.get("group_id")
        group = Group.objects.get(id=group_id)
        num_yes_votes = group.votes.filter(choice=VoteType.YES, show=show).count()
        return num_yes_votes

    def get_num_maybe_votes(self, show):
        group_id = self.context.get("group_id")
        group = Group.objects.get(id=group_id)
        num_yes_votes = group.votes.filter(choice=VoteType.MAYBE, show=show).count()
        return num_yes_votes

    def get_num_no_votes(self, show):
        group_id = self.context.get("group_id")
        group = Group.objects.get(id=group_id)
        num_yes_votes = group.votes.filter(choice=VoteType.NO, show=show).count()
        return num_yes_votes
