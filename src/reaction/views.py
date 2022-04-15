import json

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from episode_detail.models import EpisodeDetail
from friendship.models import Friend
from reaction.serializers import ReactionDetailSerializer
from reaction.serializers import ReactionSerializer
from rest_framework import generics
from show.models import Show
from show.serializers import ShowSeasonDetailSerializer

from .models import Reaction
from .models import VisibilityChoice


class ReactionsPerEpisodeForShow(generics.GenericAPIView):
    queryset = Reaction.objects.all()
    serializer_class = ShowSeasonDetailSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        """
        Given show id, get shortened list of reactions (in this case max 10 reactions).
        Visibility of reactions by default is PUBLIC.
        """
        show = Show.objects.get(id=pk)
        serializer = self.serializer_class(show, context={"request": request})
        return success_response(serializer.data)


class ReactionsForEpisode(generics.GenericAPIView):
    queryset = Reaction.objects.all()
    serializer_class = ReactionDetailSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request):
        """
        Get all (relevant) reactions for one episode
        {
            "episode_id": <>,
            "filter_by":  "public" or "friends" or ""
        }
        """
        data = json.loads(request.body)
        episode_id = data.get("episode_id")
        filter_by = data.get("filter_by").lower()

        if not filter_by:
            public_reactions = Reaction.objects.filter(episode__id=episode_id, visibility=VisibilityChoice.PUBLIC)
            friends = [friend.profile for friend in Friend.objects.friends(user=request.user)]
            friend_reactions = Reaction.objects.filter(
                episode__id=episode_id, visibility=VisibilityChoice.FRIENDS, author__in=friends
            )
            user_reactions = Reaction.objects.filter(episode__id=episode_id, author=request.user.profile)
            reactions = public_reactions | friend_reactions | user_reactions
        elif filter_by == VisibilityChoice.PUBLIC:
            reactions = Reaction.objects.filter(episode__id=episode_id, visibility=VisibilityChoice.PUBLIC)
        elif filter_by == VisibilityChoice.FRIENDS:
            friends = [friend.profile for friend in Friend.objects.friends(user=request.user)]
            reactions = Reaction.objects.filter(
                episode__id=episode_id, visibility=VisibilityChoice.FRIENDS, author__in=friends
            )
        else:
            return failure_response(f"filter_by must be '{VisibilityChoice.PUBLIC}' or '{VisibilityChoice.FRIENDS}'!")
        serializer = self.serializer_class(reactions, many=True, context={"request": request})
        return success_response(serializer.data)


class ReactionDetail(generics.GenericAPIView):
    queryset = Reaction.objects.all()
    serializer_class = ReactionDetailSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        """Get a reaction by id. Comes with thoughts and has_liked."""
        if not Reaction.objects.filter(pk=pk):
            return failure_response(f"Reaction of id {pk} does not exist.")
        reaction = Reaction.objects.get(pk=pk)
        return success_response(self.serializer_class(reaction, context={"request": request}).data)


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
            "visibility": "public" or "friends"
        }
        """
        data = json.loads(request.body)
        episode_id = data.get("episode_id")
        if not EpisodeDetail.objects.filter(id=episode_id).exists():
            return failure_response(f"Episode with id {episode_id} does not exist!")
        if request is None:
            return failure_response("request is None")
        text = data.get("text")
        reaction = Reaction(episode=EpisodeDetail.objects.get(id=episode_id), text=text, author=request.user.profile)
        visibility = data.get("visibility")
        if visibility == VisibilityChoice.PUBLIC:
            reaction.visibility = VisibilityChoice.PUBLIC
        elif visibility == VisibilityChoice.FRIENDS:
            reaction.visibility = VisibilityChoice.FRIENDS
        reaction.save()
        serializer = self.serializer_class(reaction, context={"request": request})
        return success_response(serializer.data)


class ReactionRemove(generics.GenericAPIView):

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        if not Reaction.objects.filter(id=pk).exists():
            return failure_response(f"Reaction with id {pk} does not exist!")
        reaction = Reaction.objects.get(id=pk)
        if reaction.author.user != request.user:
            return failure_response(f"User {request.user.id} is not authorized to delete reaction {pk}!")
        reaction.delete()
        return success_response()
