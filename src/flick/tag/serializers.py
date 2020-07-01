from rest_framework import serializers

from .models import Tag

from show.simple_serializers import ShowSimpleSerializer


class TagSerializer(serializers.ModelSerializer):
    tag_id = serializers.CharField(source="id")

    class Meta:
        model = Tag
        fields = ("tag_id", "tag")
        read_only_fields = fields


class TagDetailSerializer(serializers.ModelSerializer):
    tag_id = serializers.CharField(source="id")
    shows = ShowSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ("tag_id", "tag", "shows")
        read_only_fields = fields
