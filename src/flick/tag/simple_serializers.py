from rest_framework import serializers

from .models import Tag


class TagSimpleSerializer(serializers.ModelSerializer):
    tag_id = serializers.CharField(source="id")

    class Meta:
        model = Tag
        fields = ("tag_id", "tag")
        read_only_fields = fields
