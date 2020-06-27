from asset.serializers import AssetBundleDetailSerializer

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from show.simple_serializers import ShowSimpleSerializer
from show.serializers import ShowSerializer
from tag.serializers import TagSerializer


from .models import Lst


class LstSimpleSerializer(ModelSerializer):
    shows = ShowSerializer(many=True)

    class Meta:
        model = Lst
        fields = ("id", "lst_name", "lst_pic", "is_favorite", "is_private", "is_watched", "shows")
        read_only_fields = fields
