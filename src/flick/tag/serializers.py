from rest_framework.serializers import CurrentUserDefault, ModelSerializer, PrimaryKeyRelatedField

from .models import Tag

from show.simple_serializers import ShowSimpleSerializer


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "tag")
        read_only_fields = fields


class TagDetailSerializer(ModelSerializer):
    shows = ShowSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ("id", "tag", "shows")
        read_only_fields = fields
