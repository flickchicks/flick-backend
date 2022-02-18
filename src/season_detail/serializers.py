from episode_detail.serializers import EpisodeDetailSerializer
from rest_framework import serializers
from season_detail.models import SeasonDetail


class SeasonDetailSerializer(serializers.ModelSerializer):
    episode_details = EpisodeDetailSerializer(read_only=True, many=True)

    class Meta:
        model = SeasonDetail
        fields = ("season_num", "episode_count", "ext_api_id", "poster_pic", "overview", "episode_details")
