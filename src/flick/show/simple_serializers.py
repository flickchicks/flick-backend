from django.contrib.auth.models import User

from rest_framework.serializers import CurrentUserDefault, ModelSerializer, PrimaryKeyRelatedField

from .models import Show
from asset.serializers import AssetBundleDetailSerializer


class ShowSimpleSerializer(ModelSerializer):
    class Meta:
        model = Show
        fields = ("id", "title", "poster_pic", "directors", "is_tv")
        read_only_fields = ("id",)
