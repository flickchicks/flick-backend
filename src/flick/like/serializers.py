from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers

from .models import Like


class LikeSerializer(serializers.ModelSerializer):
    liker = ProfileSimpleSerializer(many=False)

    class Meta:
        model = Like
        fields = ("liker", "created_at")
        read_only_fields = fields
