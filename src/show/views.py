from datetime import datetime
from datetime import timedelta
import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from flick.tasks import populate_show_details
from friendship.models import Friend
import pytz
from reaction.models import Reaction
from reaction.serializers import ReactionFriendsProgressSerializer
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets

from .models import Show
from .serializers import ShowSerializer
from .tasks import add_show_to_lsts


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

    def is_tv_and_has_no_episode_detail_info(self, show):
        if not show.is_tv:
            return False
        seasons_detail = show.season_details.first()
        episode_detail = seasons_detail.episode_details.first()
        return episode_detail is None or episode_detail.name is None

    def seasons_or_episode_details_incomplete(self, show):
        return not show.season_details.exists() or self.is_tv_and_has_no_episode_detail_info(show)

    def get(self, request, pk):
        """Get a specific show by id. Comes with user rating, friend rating, and comments."""
        try:
            if not Show.objects.filter(pk=pk):
                return failure_response(f"Show of id {pk} does not exist.")
            show = Show.objects.get(pk=pk)
            utc = pytz.utc
            delta = datetime.now(tz=utc) - show.updated_at
            if delta > timedelta(days=7) or self.seasons_or_episode_details_incomplete(show):
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


class AddShowToListsView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        """
        Add one show to a multiple lists.
        """
        data = json.loads(request.body)
        list_ids = data.get("list_ids")
        add_show_to_lsts.delay(show_id=pk, list_ids=list_ids, user_id=request.user.id)
        return success_response()


class ShowFriendProgressView(generics.GenericAPIView):
    def get(self, request, pk):
        friends = Friend.objects.friends(user=request.user)
        friend_reactions = Reaction.objects.filter(episode__season__show__id=pk).filter(author__user__in=friends)
        friends_with_reactions = friend_reactions.values_list("author__id", flat=True).distinct().order_by()
        lastest_reactions = []
        for friend in friends_with_reactions:
            friend_latest_reaction = (
                friend_reactions.filter(author=friend)
                .order_by("-episode__episode_num", "-episode__season__season_num")
                .first()
            )
            lastest_reactions.append(friend_latest_reaction)
        serializer = ReactionFriendsProgressSerializer(instance=lastest_reactions, many=True)
        return success_response(serializer.data)
