import datetime
import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from flick.tasks import populate_show_details
from lst.models import Lst
from lst.serializers import LstWithSimpleShowsSerializer
import pytz
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
        try:
            if not Show.objects.filter(pk=pk):
                return failure_response(f"Show of id {pk} does not exist.")
            show = Show.objects.get(pk=pk)
            utc = pytz.utc
            delta = datetime.datetime.now(tz=utc) - show.updated_at
            minutes = (delta.total_seconds() % 3600) // 60
            if minutes > 30:
                populate_show_details(show.id)
        except Exception as e:
            return failure_response(message=f"Oh no! {e}")
        return success_response(self.serializer_class(show, context={"request": request}).data)

    def post(self, request, pk):
        """Allows users to write a rating and/or comment."""
        if not Show.objects.filter(pk=pk):
            return failure_response(f"Show of id {pk} does not exist.")
        show = Show.objects.get(pk=pk)
        user = request.user
        profile = Profile.objects.get(user=user)
        data = json.loads(request.body)
        score = data.get("user_rating")
        comment_info = data.get("comment")

        if score:
            existing_rating = show.ratings.filter(rater=user)
            if existing_rating:
                existing_rating = show.ratings.get(rater=user)
                existing_rating.score = score
                existing_rating.save()
            else:
                show.ratings.create(score=score, rater=user)
            show.save()

        if comment_info:
            message = comment_info.get("message")
            is_spoiler = comment_info.get("is_spoiler")
            show.comments.create(message=message, is_spoiler=is_spoiler, owner=profile)
            show.save()

        return success_response(self.serializer_class(show, context={"request": request}).data)


class AddToListView(generics.GenericAPIView):

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        data = json.loads(request.body)
        list_ids = data.get("list_ids")
        if not Show.objects.filter(pk=pk):
            return failure_response(f"show with id {pk} does not exist")

        show = Show.objects.get(pk=pk)
        success_lists = []
        for lst_id in list_ids:
            lst = Lst.objects.filter(pk=lst_id)
            if lst:
                lst = Lst.objects.get(pk=lst_id)
                user_profile = Profile.objects.get(user=request.user)
                is_owner = user_profile == lst.owner
                is_collaborator = user_profile in lst.collaborators.all()
                if not is_owner and not is_collaborator:
                    continue
                lst.shows.add(show)
                success_lists.append(lst)

        return success_response(
            LstWithSimpleShowsSerializer(success_lists, many=True, context={"request": request}).data
        )
