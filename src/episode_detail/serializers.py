from episode_detail.models import EpisodeDetail
from friendship.models import Friend
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
        serializer_context = {"request": self.context.get("request")}
        request_user = serializer_context["request"].user
        public_reactions = obj.reactions.filter(visibility=VisibilityChoice.PUBLIC)
        friends = [friend.profile for friend in Friend.objects.friends(user=request_user)]
        friend_reactions = obj.reactions.filter(visibility=VisibilityChoice.FRIENDS, author__in=friends)
        user_reactions = obj.reactions.filter(author=request_user.profile)
        reactions = public_reactions | friend_reactions | user_reactions
        reactions = reactions.order_by("-updated_at", "author")

        if reactions.count() < 10:
            return ReactionSerializer(instance=reactions, many=True, context=serializer_context).data
        else:
            authors = reactions.values_list("author", flat=True).distinct()[:10]
            distinct_reactions, reaction_ids = [], []
            for author in authors:
                reaction = reactions.filter(author=author).first()
                distinct_reactions.append(reaction), reaction_ids.append(reaction.id)
            additional_reactions = reactions.exclude(id__in=reaction_ids)[: 10 - authors.count()]
            return ReactionSerializer(
                instance=distinct_reactions + list(additional_reactions), many=True, context=serializer_context
            ).data

    class Meta:
        model = EpisodeDetail
        fields = ("id", "ext_api_id", "episode_num", "name", "overview", "reactions", "is_default")
