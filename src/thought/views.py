import json

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from reaction.models import Reaction
from rest_framework import generics

from .models import Thought
from .serializers import ThoughtSerializer


class ThoughtAdd(generics.GenericAPIView):

    queryset = Thought.objects.all()
    serializer_class = ThoughtSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request):
        """
        Create a thought
        {
            "reaction_id": <>
            "text": <>,
        }
        """
        data = json.loads(request.body)
        reaction_id = data.get("reaction_id")
        if not Reaction.objects.filter(id=reaction_id).exists():
            return failure_response(f"Episode with id {reaction_id} does not exist!")
        reaction = Reaction.objects.get(id=reaction_id)
        text = data.get("text")
        thought = Thought(reaction=reaction, text=text, author=request.user.profile)
        thought.save()
        serializer = self.serializer_class(thought)
        return success_response(serializer.data)


class ThoughtRemove(generics.GenericAPIView):

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        if not Thought.objects.filter(id=pk).exists():
            return failure_response(f"Thought with id {pk} does not exist!")
        thought = Thought.objects.get(id=pk)
        if thought.author.user != request.user:
            return failure_response(f"User {request.user.id} is not authorized to delete thought {pk}!")
        Thought.delete()
        return success_response()
