from user.profile_simple_serializers import ProfileSimpleSerializer

from comment.serializers import SimpleCommentSerializer
from lst.serializers import LstWithSimpleShowsSerializer
from rest_framework import serializers
from show.simple_serializers import ShowSimpleSerializer

from .models import Discover


class DiscoverSerializer(serializers.ModelSerializer):
    friend_recommendations = ProfileSimpleSerializer(many=True)
    list_recommendations = LstWithSimpleShowsSerializer(many=True)
    show_recommendations = ShowSimpleSerializer(many=True)
    friend_comments = SimpleCommentSerializer(many=True)

    class Meta:
        model = Discover
        fields = ("friend_recommendations", "list_recommendations", "show_recommendations", "friend_comments")
        ready_only_fields = fields
