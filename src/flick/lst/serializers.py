from asset.serializers import AssetBundleDetailSerializer

# from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import CurrentUserDefault, ModelSerializer, PrimaryKeyRelatedField

from tag.serializers import TagSerializer

from .models import Lst


class LstSerializer(ModelSerializer):
    class Meta:
        model = Lst
        fields = (
            "id",
            "lst_name",
            "lst_pic",
            "is_favorite",
            "is_private",
            "is_watched",
            # "collaborator",
            # "owner",
            # "shows",
        )
        read_only_fields = fields
