from django.contrib.auth.models import User

from rest_framework.serializers import CurrentUserDefault, ModelSerializer, PrimaryKeyRelatedField

from .models import Show
from asset.serializers import AssetBundleDetailSerializer
from user.serializers import UserSerializer


class ShowSimpleSerializer(ModelSerializer):
    # CurrentUserDefault is basically request.data (the authenticated user related to this request)

    class Meta:
        model = Show
        fields = ("id", "title", "poster_pic", "director", "is_tv")
        read_only_fields = ("id",)
