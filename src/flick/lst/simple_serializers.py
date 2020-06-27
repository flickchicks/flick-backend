from rest_framework import serializers

from .models import Lst
from asset.serializers import AssetBundleDetailSerializer
from show.simple_serializers import ShowSimpleSerializer
from show.serializers import ShowSerializer
from tag.serializers import TagSerializer


class LstSimpleSerializer(serializers.ModelSerializer):
    shows = ShowSerializer(many=True)
    lst_id = serializers.CharField(source="id")

    class Meta:
        model = Lst
        fields = ("lst_id", "lst_name", "lst_pic", "is_favorite", "is_private", "is_watched", "shows")
        read_only_fields = fields
