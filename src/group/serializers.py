from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers
from show.serializers import ShowSearchSerializer

from .models import Group


class GroupSimpleSerializer(serializers.ModelSerializer):
    members = ProfileSimpleSerializer(many=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "members",
        )
        read_only_fields = fields


class GroupSerializer(serializers.ModelSerializer):
    members = ProfileSimpleSerializer(many=True)
    shows = ShowSearchSerializer(many=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "members",
            "shows",
        )
        read_only_fields = fields
