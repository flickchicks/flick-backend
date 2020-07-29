import json

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets

from .models import Show
from .serializers import ShowSerializer


class ShowViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    See all possible shows.
    Will not include seeing user specific details like ratings and comments.
    """

    queryset = Show.objects.all()
    serializer_class = ShowSerializer

    permission_classes = api_settings.STANDARD_PERMISSIONS


class ShowDetail(generics.GenericAPIView):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        """Get a specific show by id. Comes with user rating, friend rating, and comments."""
        if not Show.objects.filter(pk=pk):
            return failure_response(f"Show of id {pk} does not exist.")
        show = Show.objects.get(pk=pk)
        return success_response(self.serializer_class(show, context={"request": request}).data)

    def post(self, request, pk):
        """Allows users to write a rating and/or comment."""
        if not Show.objects.filter(pk=pk):
            return failure_response(f"Show of id {pk} does not exist.")
        show = Show.objects.get(pk=pk)

        user = request.user
        data = json.loads(request.body)
        score = data.get("user_rating")

        if score:
            show.ratings.create(score=score, rater=user)
            show.save()

        return success_response(self.serializer_class(show, context={"request": request}).data)
