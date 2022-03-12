from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers

from .models import Thought


class ThoughtSerializer(serializers.ModelSerializer):
    owner = ProfileSimpleSerializer(many=False)
    has_liked = serializers.SerializerMethodField(method_name="get_has_liked")

    class Meta:
        model = Thought
        fields = ("created_at", "id", "num_likes", "has_liked", "author", "text")
        read_only_fields = fields

    def get_has_liked(self, instance):
        request = self.context.get("request")
        has_liked = instance.likers.filter(liker=request.user.profile).exists()
        return has_liked
