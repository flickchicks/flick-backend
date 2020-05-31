from asset.serializers import AssetBundleDetailSerializer
from django.contrib.auth.models import User

# from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import CurrentUserDefault, ModelSerializer, PrimaryKeyRelatedField
from user.serializers import UserSerializer

from tag.serializers import TagSerializer

from .models import Show


class ShowSerializer(ModelSerializer):
    # CurrentUserDefault is basically request.data (the authenticated user related to this request)
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Show
        fields = (
            "id",
            "title",
            "poster_pic",
            "director",
            "is_tv",
            "date_released",
            "status",
            "language",
            "duration",
            "plot",
            "tags",
            "seasons",
            "audience_level",
            "imdb_rating",
            "tomato_rating",
            "friends_rating",
            "platforms",
            "keywords",
        )
        read_only_fields = ("id",)
