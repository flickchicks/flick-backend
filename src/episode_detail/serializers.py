from episode_detail.models import EpisodeDetail
from rest_framework import serializers


class EpisodeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeDetail
        fields = ("id", "ext_api_id", "episode_num", "name", "overview")
