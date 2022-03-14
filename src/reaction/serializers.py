from user.profile_simple_serializers import ProfileSimpleSerializer

from django.forms import ChoiceField
from rest_framework import serializers

from .models import Reaction
from .models import VisibilityChoice


class ReactionSerializer(serializers.ModelSerializer):
    author = ProfileSimpleSerializer(many=False)
    visibility = ChoiceField(choices=VisibilityChoice)

    class Meta:
        model = Reaction
        fields = ("id", "text", "author", "visibility", "created_at", "updated_at")
