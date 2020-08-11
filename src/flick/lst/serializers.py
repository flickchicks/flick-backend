from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers
from show.serializers import ShowSearchSerializer
from tag.simple_serializers import TagSimpleSerializer

from .models import Lst


class LstSerializer(serializers.ModelSerializer):
    collaborators = ProfileSimpleSerializer(many=True)
    owner = ProfileSimpleSerializer(many=False)
    shows = ShowSearchSerializer(many=True)
    lst_id = serializers.CharField(source="id")
    tags = TagSimpleSerializer(many=True)

    class Meta:
        model = Lst
        fields = (
            "lst_id",
            "lst_name",
            "lst_pic",
            "is_saved",
            "is_private",
            "is_watch_later",
            "collaborators",
            "owner",
            "shows",
            "tags",
        )
        read_only_fields = fields
