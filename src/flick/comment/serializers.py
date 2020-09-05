from user.models import Profile
from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    owner = ProfileSimpleSerializer(many=False)
    has_liked = serializers.SerializerMethodField(method_name="get_has_liked")
    has_read = serializers.SerializerMethodField(method_name="get_has_read")

    class Meta:
        model = Comment
        fields = ("created_at", "id", "is_spoiler", "num_likes", "has_liked", "has_read", "owner", "message")
        read_only_fields = fields

    def get_has_liked(self, instance):
        request = self.context.get("request")
        user = request.user

        if not Profile.objects.filter(user=user):
            return False
        profile = Profile.objects.get(user=user)

        has_liked = instance.likers.filter(liker=profile).exists()
        return has_liked

    def get_has_read(self, instance):
        if not instance.is_spoiler:
            return True
        request = self.context.get("request")
        user = request.user

        if not Profile.objects.filter(user=user):
            return False
        profile = Profile.objects.get(user=user)
        if instance.owner == profile:
            return True

        has_read = instance.reads.filter(reader=profile).exists()
        return has_read
