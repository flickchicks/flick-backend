from rest_framework.serializers import CurrentUserDefault, ModelSerializer, PrimaryKeyRelatedField

from .models import Tag


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "tag")
        read_only_fields = fields
