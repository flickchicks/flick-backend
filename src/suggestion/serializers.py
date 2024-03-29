from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers
from show.serializers import ShowSearchSerializer
from show.simple_serializers import ShowSimpleSerializer

from .models import PrivateSuggestion
from .models import PublicSuggestion


class PrivateSuggestionSerializer(serializers.ModelSerializer):
    to_user = ProfileSimpleSerializer(many=False)
    from_user = ProfileSimpleSerializer(many=False)
    show = ShowSearchSerializer(many=False)
    has_liked = serializers.SerializerMethodField(method_name="get_has_liked")

    class Meta:
        model = PrivateSuggestion
        fields = ("id", "to_user", "from_user", "show", "message", "has_liked", "created_at", "updated_at")
        read_only_fields = fields

    def get_has_liked(self, instance):
        request = self.context.get("request")
        has_liked = instance.likers.filter(liker__user=request.user).exists()
        return has_liked


class SimpleSuggestionSerializer(serializers.ModelSerializer):
    to_user = ProfileSimpleSerializer(many=False)
    from_user = ProfileSimpleSerializer(many=False)
    show = ShowSimpleSerializer(many=False)

    class Meta:
        model = PrivateSuggestion
        fields = ("id", "message", "show", "to_user", "from_user", "updated_at", "created_at")
        read_only_fields = fields


class PublicSuggestionSerializer(serializers.ModelSerializer):
    author = ProfileSimpleSerializer(many=False)
    show = ShowSearchSerializer(many=False)

    class Meta:
        model = PublicSuggestion
        fields = ("author", "show", "message", "created_at", "updated_at")
        read_only_fields = fields
