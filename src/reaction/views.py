import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from episode_detail.models import EpisodeDetail
from reaction.serializers import ReactionSerializer
from rest_framework import generics

from .models import Reaction


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
        profile = Profile.objects.get(user=request.user)
        data = json.loads(request.body)
        episode_id = data.get("episode_id")
        if not EpisodeDetail.objects.filter(id=episode_id).exists():
            return failure_response(f"Episode with id {episode_id} does not exist!")
        text = data.get("text")
        reaction = Reaction(episode=EpisodeDetail.objects.get(id=episode_id), text=text, author=profile)
        reaction.save()
        serializer = self.serializer_class(reaction)
        return success_response(serializer.data)


class ReactionDelete(generics.GenericAPIView):

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        """
        Delete a reaction
        """
        profile = Profile.objects.get(user=request.user)
        if not Reaction.objects.filter(id=pk).exists():
            return failure_response(f"Reaction with id {pk} does not exist!")
        reaction = Reaction.objects.get(id=pk)
        if not reaction.author == profile:
            return failure_response(f"User {profile.id} is not authorized to delete reaction {pk}!")
        reaction.delete()
        return success_response()
