from episode_detail.serializers import EpisodeDetailSerializer
from episode_detail.serializers import EpisodeDetailShortenedReactionsSerializer
from rest_framework import serializers
from season_detail.models import SeasonDetail


class SeasonDetailSerializer(serializers.ModelSerializer):
    episode_details = EpisodeDetailSerializer(read_only=True, many=True)

    class Meta:
        model = SeasonDetail
        fields = ("id", "season_num", "episode_count", "ext_api_id", "poster_pic", "overview", "episode_details")


class SeasonDetailShortenedEpisodeDetailsSerializer(serializers.ModelSerializer):
    episode_details = EpisodeDetailShortenedReactionsSerializer(many=True)

    class Meta:
        model = SeasonDetail
        fields = ("id", "episode_details")
        read_only_fields = fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["episode_details"].context.update(self.context)
