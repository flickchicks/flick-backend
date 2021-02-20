from user.models import Profile
from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers
from show.serializers import ShowSearchSerializer

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
        user = request.user
        profile = Profile.objects.get(user=user)
        has_liked = instance.likers.filter(liker=profile).exists()
        return has_liked


class PublicSuggestionSerializer(serializers.ModelSerializer):
    author = ProfileSimpleSerializer(many=False)
    show = ShowSearchSerializer(many=False)

    class Meta:
        model = PublicSuggestion
        fields = ("author", "show", "message", "created_at", "updated_at")
        read_only_fields = fields
