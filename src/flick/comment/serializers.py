from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    comment_id = serializers.CharField(source="id", read_only=True)
    owner = ProfileSimpleSerializer(many=False)

    class Meta:
        model = Comment
        fields = (
            "created_at",
            "comment_id",
            "is_spoiler",
            "num_likes",
            "owner",
            "text",
        )
        read_only_fields = fields
