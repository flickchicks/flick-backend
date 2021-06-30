from django.core.paginator import Paginator
from lst.simple_serializers import LstSimpleSerializer
from rest_framework import serializers
from show.simple_serializers import ShowSimpleSerializer

from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    # shows = ShowSimpleSerializer(many=True, read_only=True)
    lsts = LstSimpleSerializer(many=True, read_only=True)
    shows = serializers.SerializerMethodField("paginated_shows")

    def paginated_shows(self, obj):
        paginator = Paginator(obj.shows.all(), 3)
        show_page = paginator.page(1)
        serializer = ShowSimpleSerializer(show_page, many=True)
        return serializer.data

    class Meta:
        model = Tag
        fields = ("id", "ext_api_genre_id", "name", "shows", "lsts")
        read_only_fields = fields
