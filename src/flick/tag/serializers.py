from lst.simple_serializers import LstSimpleSerializer
from rest_framework import serializers
from show.simple_serializers import ShowSimpleSerializer

from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    shows = ShowSimpleSerializer(many=True, read_only=True)
    lsts = LstSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ("id", "ext_api_genre_id", "name", "shows", "lsts")
        read_only_fields = fields
