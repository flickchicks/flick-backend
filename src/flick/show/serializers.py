from rest_framework.serializers import ModelSerializer
from tag.simple_serializers import TagSimpleSerializer

from .models import Show


class ShowSerializer(ModelSerializer):
    # CurrentUserDefault is basically request.data (the authenticated user related to this request)
    tags = TagSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = Show
        fields = (
            "id",
            "title",
            "poster_pic",
            "directors",
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
            "cast",
        )
        read_only_fields = ("id",)
