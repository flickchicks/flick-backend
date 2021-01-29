from user.profile_simple_serializers import ProfileSimpleSerializer

from like.serializers import LikeSerializer
from rest_framework import serializers
from show.serializers import ShowSearchSerializer
from show.simple_serializers import ShowSimplestSerializer
from tag.simple_serializers import TagSimpleSerializer

from .models import Lst


class LstSerializer(serializers.ModelSerializer):
    collaborators = ProfileSimpleSerializer(many=True)
    owner = ProfileSimpleSerializer(many=False)
    shows = ShowSearchSerializer(many=True)
    tags = TagSimpleSerializer(many=True)
    likers = LikeSerializer(many=True)

    class Meta:
        model = Lst
        fields = (
            "id",
            "name",
            "pic",
            "description",
            "is_saved",
            "is_private",
            "is_watch_later",
            "collaborators",
            "owner",
            "shows",
            "tags",
            "num_likes",
            "likers",
        )
        read_only_fields = fields


class LstWithSimpleShowsSerializer(serializers.ModelSerializer):
    collaborators = ProfileSimpleSerializer(many=True)
    owner = ProfileSimpleSerializer(many=False)
    shows = ShowSimplestSerializer(many=True)
    tags = TagSimpleSerializer(many=True)
    likers = LikeSerializer(many=True)

    class Meta:
        model = Lst
        fields = (
            "id",
            "name",
            "pic",
            "description",
            "is_saved",
            "is_private",
            "is_watch_later",
            "collaborators",
            "owner",
            "shows",
            "tags",
            "num_likes",
            "likers",
        )
        read_only_fields = fields
