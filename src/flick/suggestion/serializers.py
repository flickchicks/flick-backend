from user.profile_simple_serializers import ProfileSimpleSerializer

from django.contrib.auth.models import User
from rest_framework import serializers
from show.serializers import ShowSearchSerializer

from .models import PrivateSuggestion
from .models import PublicSuggestion


class PrivateSuggestionUserSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source="id")
    name = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = (User.USERNAME_FIELD, "user_id", "name")
        write_only_fields = fields


class PrivateSuggestionSerializer(serializers.ModelSerializer):
    to_user = PrivateSuggestionUserSerializer(many=False)
    from_user = ProfileSimpleSerializer(many=False)
    show = ShowSearchSerializer(many=False)

    class Meta:
        model = PrivateSuggestion
        fields = ("to_user", "from_user", "show", "message", "created_at")
        read_only_fields = fields


class PublicSuggestionSerializer(serializers.ModelSerializer):
    author = ProfileSimpleSerializer(many=False)
    show = ShowSearchSerializer(many=False)

    class Meta:
        model = PublicSuggestion
        fields = ("author", "show", "message", "created_at")
        read_only_fields = fields
