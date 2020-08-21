from rest_framework.serializers import ModelSerializer

from .models import Show


class ShowSimpleSerializer(ModelSerializer):
    class Meta:
        model = Show
        fields = ("id", "title", "poster_pic", "directors", "is_tv")
        read_only_fields = fields


class ShowSimplestSerializer(ModelSerializer):
    class Meta:
        model = Show
        fields = ("id", "title", "poster_pic")
        read_only_fields = fields
