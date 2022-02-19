import json

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from episode_detail.models import EpisodeDetail
from friendship.models import Friend
from reaction.serializers import ReactionSerializer
from rest_framework import generics

from .models import Reaction
from .models import VisibilityChoice


class ReactionsForEpisode(generics.GenericAPIView):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request):
        """
        Get all (relevant) reactions for one episode
        {
            "episode_id": <>,
            "filter_by":  "public" or "friends"
        }
        """
        data = json.loads(request.body)
        episode_id = data.get("episode_id")
        filter_by = data.get("filter_by").lower()
        if filter_by == VisibilityChoice.PUBLIC:
            reactions = Reaction.objects.filter(episode__id=episode_id, visibility=VisibilityChoice.PUBLIC)
        elif filter_by == VisibilityChoice.FRIENDS:
            friends = [friend.profile for friend in Friend.objects.friends(user=request.user)]
            reactions = Reaction.objects.filter(
                episode__id=episode_id, visibility=VisibilityChoice.FRIENDS, author__in=friends
            )
        else:
            return failure_response(f"filter_by must be '{VisibilityChoice.PUBLIC}' or '{VisibilityChoice.FRIENDS}'!")
        serializer = self.serializer_class(reactions, many=True)
        return success_response(serializer.data)


class ReactionAdd(generics.GenericAPIView):

    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request):
        """
        Create a reaction
        {
            "episode_id": <>
            "text": <>,
        }
        """
        data = json.loads(request.body)
        episode_id = data.get("episode_id")
        if not EpisodeDetail.objects.filter(id=episode_id).exists():
            return failure_response(f"Episode with id {episode_id} does not exist!")
        text = data.get("text")
        reaction = Reaction(episode=EpisodeDetail.objects.get(id=episode_id), text=text, author=request.user.profile)
        reaction.save()
        serializer = self.serializer_class(reaction)
        return success_response(serializer.data)
