from user.profile_simple_serializers import ProfileSimpleSerializer

from django.forms import ChoiceField
from rest_framework import serializers
from thought.serializers import ThoughtSerializer

from .models import Reaction
from .models import VisibilityChoice


class ReactionSerializer(serializers.ModelSerializer):
    author = ProfileSimpleSerializer(many=False)
    visibility = ChoiceField(choices=VisibilityChoice)
    has_liked = serializers.SerializerMethodField(method_name="get_has_liked")

    class Meta:
        model = Reaction
        fields = ("id", "text", "author", "visibility", "has_liked", "created_at", "updated_at")

    def get_has_liked(self, instance):
        request = self.context.get("request")
        has_liked = instance.likers.filter(liker=request.user.profile).exists()
        return has_liked


class ReactionDetailSerializer(serializers.ModelSerializer):
    author = ProfileSimpleSerializer(many=False)
    visibility = ChoiceField(choices=VisibilityChoice)
    thoughts = ThoughtSerializer(read_only=True, many=True)
    has_liked = serializers.SerializerMethodField(method_name="get_has_liked")

    class Meta:
        model = Reaction
        fields = (
            "id",
            "text",
            "author",
            "visibility",
            "num_likes",
            "has_liked",
            "thoughts",
            "created_at",
            "updated_at",
        )

    def get_has_liked(self, instance):
        request = self.context.get("request")
        has_liked = instance.likers.filter(liker=request.user.profile).exists()
        return has_liked
