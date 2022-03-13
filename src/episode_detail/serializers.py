from episode_detail.models import EpisodeDetail
from reaction.models import VisibilityChoice
from reaction.serializers import ReactionSerializer
from rest_framework import serializers


class EpisodeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpisodeDetail
        fields = ("id", "ext_api_id", "episode_num", "name", "overview", "is_default")


class EpisodeDetailShortenedReactionsSerializer(serializers.ModelSerializer):
    reactions = serializers.SerializerMethodField("get_subset_of_reactions")

    def get_subset_of_reactions(self, obj):
        reactions = obj.reactions.filter(visibility=VisibilityChoice.PUBLIC).order_by("author")
        if reactions.count() < 10:
            return ReactionSerializer(instance=reactions, many=True).data
        else:
            distinct_reactions, reaction_ids, author_ids = [], [], []
            for reaction in reactions:
                if reaction.author.id not in author_ids:
                    author_ids.append(reaction.author.id)
                    reaction_ids.append(reaction.id)
                    distinct_reactions.append(reaction)
            if len(distinct_reactions) < 10:
                additional_reactions = reactions.exclude(id__in=reaction_ids)[: 10 - len(distinct_reactions)]

            return ReactionSerializer(instance=distinct_reactions + list(additional_reactions), many=True).data

    class Meta:
        model = EpisodeDetail
        fields = ("id", "ext_api_id", "episode_num", "name", "overview", "reactions", "is_default")
