from episode_detail.models import EpisodeDetail
from reaction.models import VisibilityChoice
from reaction.serializers import ReactionSerializer
from rest_framework import serializers


class EpisodeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeDetail
        fields = ("id", "ext_api_id", "episode_num", "name", "overview")


class EpisodeDetailShortenedReactionsSerializer(serializers.ModelSerializer):
    reactions = serializers.SerializerMethodField("get_subset_of_reactions")

    def get_subset_of_reactions(self, obj):
        reactions = obj.reactions.filter(visibility=VisibilityChoice.PUBLIC)[:10]
        return ReactionSerializer(instance=reactions, many=True).data

    class Meta:
        model = EpisodeDetail
        fields = ("id", "ext_api_id", "episode_num", "name", "overview", "reactions")
