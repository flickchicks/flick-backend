from episode_detail.models import EpisodeDetail
from rest_framework import serializers


class EpisodeSimpleSerializer(serializers.ModelSerializer):
    season_num = serializers.IntegerField(source="season.season_num")

    class Meta:
        model = EpisodeDetail
        fields = ("id", "season_num", "episode_num")
