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
        reactions = obj.reactions.filter(visibility=VisibilityChoice.PUBLIC).order_by("author", "-updated_at")
        if reactions.count() < 10:
            return ReactionSerializer(instance=reactions, many=True).data
        else:
            authors = reactions.values_list("author", flat=True).distinct()[:10]
            distinct_reactions, reaction_ids = [], []
            for author in authors:
                reaction = reactions.filter(author=author).first()
                distinct_reactions.append(reaction), reaction_ids.append(reaction.id)
            if authors.count() < 10:
                additional_reactions = reactions.exclude(id__in=reaction_ids)[: 10 - authors.count()]
            return ReactionSerializer(instance=distinct_reactions + list(additional_reactions), many=True).data

    class Meta:
        model = EpisodeDetail
        fields = ("id", "ext_api_id", "episode_num", "name", "overview", "reactions", "is_default")
