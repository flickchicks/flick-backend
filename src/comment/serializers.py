from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers
from show.simple_serializers import ShowDiscoverSerializer
from show.simple_serializers import ShowSimpleSerializer

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    owner = ProfileSimpleSerializer(many=False)
    has_liked = serializers.SerializerMethodField(method_name="get_has_liked")
    is_readable = serializers.SerializerMethodField(method_name="get_is_readable")

    class Meta:
        model = Comment
        fields = ("created_at", "id", "is_spoiler", "num_likes", "has_liked", "is_readable", "owner", "message")
        read_only_fields = fields

    def get_has_liked(self, instance):
        request = self.context.get("request")
        has_liked = instance.likers.filter(liker=request.user.profile).exists()
        return has_liked

    def get_is_readable(self, instance):
        if not instance.is_spoiler:
            return True
        request = self.context.get("request")
        profile = request.user.profile
        if instance.owner == profile:
            return True
        is_readable = instance.reads.filter(reader=profile).exists()
        return is_readable


class SimpleCommentSerializer(serializers.ModelSerializer):
    owner = ProfileSimpleSerializer(many=False)
    show = ShowSimpleSerializer(many=False)

    class Meta:
        model = Comment
        fields = ("created_at", "id", "is_spoiler", "num_likes", "owner", "message", "show")
        read_only_fields = fields


class CommentDiscoverSerializer(serializers.ModelSerializer):
    owner = ProfileSimpleSerializer(many=False)
    show = ShowDiscoverSerializer(many=False)

    class Meta:
        model = Comment
        fields = ("created_at", "id", "is_spoiler", "num_likes", "owner", "message", "show")
        read_only_fields = fields
