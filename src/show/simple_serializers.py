from rest_framework.serializers import ModelSerializer
from tag.simple_serializers import TagSimpleSerializer

from .models import Show


class ShowSimpleSerializer(ModelSerializer):
    class Meta:
        model = Show
        fields = ("id", "ext_api_id", "ext_api_source", "title", "poster_pic", "directors", "is_tv")
        read_only_fields = fields


class ShowSimplestSerializer(ModelSerializer):
    class Meta:
        model = Show
        fields = ("id", "ext_api_id", "ext_api_source", "title", "poster_pic")
        read_only_fields = fields


class ShowDiscoverSerializer(ModelSerializer):
    tags = TagSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = Show
        fields = (
            "id",
            "ext_api_id",
            "ext_api_source",
            "title",
            "poster_pic",
            "is_tv",
            "plot",
            "date_released",
            "tags",
        )
        read_only_fields = fields
