from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers
from show.serializers import ShowSearchSerializer

from .models import Vote


class VoteSerializer(serializers.ModelSerializer):
    voter = ProfileSimpleSerializer()
    show = ShowSearchSerializer()

    class Meta:
        model = Vote
        fields = ("id", "voter", "choice", "show")
        read_only_fields = fields
