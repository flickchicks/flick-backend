from rest_framework import serializers

from .models import Lst
from asset.serializers import AssetBundleDetailSerializer
from show.simple_serializers import ShowSimpleSerializer
from show.serializers import ShowSerializer
from tag.serializers import TagSerializer
from user.profile_simple_serializers import ProfileSimpleSerializer


class LstSerializer(serializers.ModelSerializer):
    collaborators = ProfileSimpleSerializer(many=True)
    owner = ProfileSimpleSerializer(many=False)
    shows = ShowSerializer(many=True)
    lst_id = serializers.CharField(source="id")

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
        )
        read_only_fields = fields
