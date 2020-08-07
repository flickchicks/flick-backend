from user.profile_simple_serializers import ProfileSimpleSerializer

from like.serializers import LikeSerializer
from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    owner = ProfileSimpleSerializer(many=False)
    likers = LikeSerializer(many=True)

    class Meta:
        model = Comment
        fields = (
            "created_at",
            "id",
            "is_spoiler",
            "num_likes",
            "likers",
            "owner",
            "message",
        )
        read_only_fields = fields
