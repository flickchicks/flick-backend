from random import sample
from user.models import Profile

from api.utils import success_response
from comment.models import Comment
from django.core.cache import caches
from django.db.models import Count
from django.db.models import Q
from friendship.models import Friend
from lst.models import Lst
from lst.models import LstSaveActivity
from lst.serializers import LstWithSimpleShowsSerializer
from rest_framework.views import APIView
from show.show_api_utils import ShowAPI
from show.simple_serializers import ShowSimpleSerializer
from show.tmdb import flicktmdb

from .models import Discover
from .serializers import DiscoverSerializer

local_cache = caches["local"]


class DiscoverView(APIView):
    api = flicktmdb()

    def get_friend_recommendations(self, user, friends):
        friends_friend = (
            Friend.objects.all()
            .filter(Q(from_user__in=friends) & ~Q(to_user=user) & ~Q(to_user__in=friends))
            .values("to_user")
        )
        most_friended_by_friends = friends_friend.annotate(Count("to_user")).order_by("-to_user__count")[:10]
        return [Profile.objects.get(user=u["to_user"]) for u in most_friended_by_friends]

    def get_trending_shows(self):
        trending_shows = local_cache.get(("trending_shows"))
        if not trending_shows:
            trending = self.api.get_trending_shows()
            trending_shows = ShowAPI.create_show_objects(trending, ShowSimpleSerializer)
            local_cache.set(("trending_shows"), trending_shows)
        trending_shows = sample(trending_shows, 10)
        return trending_shows

    def get_friend_shows(self, user_friends):
        public_lsts = Lst.objects.filter(is_private=False)
        activities = LstSaveActivity.objects.filter(lst__in=public_lsts, saved_by__in=user_friends).prefetch_related(
            "saved_by", "show", "lst"
        )
        friend_shows = activities.values_list("show", flat=True).distinct()[:10]
        return friend_shows

    def get_friend_lsts(self, user_friends):

        friend_lsts = Lst.objects.filter(
            is_private=False, is_saved=False, is_watch_later=False, owner__in=user_friends
        ).prefetch_related("shows", "owner")[:10]
        return friend_lsts

    def get_trending_lsts(self, request):
        trending_lsts = local_cache.get(("trending_lsts"))
        if not trending_lsts:
            public_lsts = (
                Lst.objects.filter(is_private=False, is_saved=False, is_watch_later=False)
                .exclude(shows=None)
                .prefetch_related("shows", "owner", "likers")
            )
            trending_lsts = public_lsts.order_by("-num_likes")[:20]
            trending_lsts = LstWithSimpleShowsSerializer(trending_lsts, many=True, context={"request": request}).data
            local_cache.set(("trending_lsts"), trending_lsts)
        trending_lsts = [lst for lst in trending_lsts if lst.get("owner").get("id") != request.user.id]
        trending_lsts = sample(trending_lsts, min(len(trending_lsts), 10))
        return trending_lsts

    def get_friend_comments(self, user_friends):
        comments = (
            Comment.objects.filter(owner__in=user_friends)
            .prefetch_related("show", "owner")
            .order_by("-created_at")[:10]
        )
        return comments

    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_anonymous:
            existing_user_discover = Discover.objects.filter(user=user).prefetch_related(
                "user",
                "friend_recommendations",
                "friend_shows",
                "friend_lsts",
                "friend_lsts__owner",
                "friend_comments",
                "friend_comments__show",
                "friend_comments__owner",
            )
            if existing_user_discover:
                user_discover = existing_user_discover[0]
                # utc = pytz.utc
                # delta = datetime.datetime.now(tz=utc) - user_discover.updated_at
                # minutes = (delta.total_seconds() % 3600) // 60
                # if minutes < 15:
                #     serializer_data = DiscoverSerializer(user_discover, context={"request": request}).data
                #     serializer_data["trending_shows"] = self.get_trending_shows()
                #     serializer_data["trending_lsts"] = self.get_trending_lsts(request)
                #     return success_response(serializer_data)
            else:
                user_discover = Discover()
                user_discover.user = user
                user_discover.save()

            friends = Friend.objects.friends(user=user)
            user_friends = [Profile.objects.get(user=friend) for friend in friends]
            user_discover.friend_recommendations.set(self.get_friend_recommendations(user, friends))
            # user_discover.friend_shows.set(self.get_friend_shows(user_friends))
            user_discover.friend_lsts.set(self.get_friend_lsts(user_friends))
            user_discover.friend_comments.set(self.get_friend_comments(user_friends))
            user_discover.save()
            serializer_data = DiscoverSerializer(user_discover, context={"request": request}).data
        else:
            serializer_data = {
                "friend_recommendations": [],
                "friend_shows": [],
                "friend_lsts": [],
                "friend_comments": [],
            }
        serializer_data["trending_shows"] = self.get_trending_shows()
        serializer_data["trending_lsts"] = self.get_trending_lsts(request)
        return success_response(serializer_data)
