import datetime
from user.models import Profile

from api import settings as api_settings
from api.utils import success_response
from comment.models import Comment
from django.core.cache import caches
from friendship.models import Friend
from lst.models import Lst
from lst.models import LstSaveActivity
import pytz
from rest_framework.views import APIView
from show.show_api_utils import ShowAPI
from show.tmdb import flicktmdb

from .models import Discover
from .serializers import DiscoverSerializer

local_cache = caches["local"]


class DiscoverShow(APIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS
    api = flicktmdb()

    def get_friend_recommendations(self, user):
        pass

    def get_trending_shows(self):
        trending = local_cache.get(("trending_shows"))
        if not trending:
            trending = self.api.get_trending_shows()
            local_cache.set(("trending_shows"), trending)
        trending_shows = ShowAPI.create_show_objects_no_serialization(trending)
        return trending_shows

    def get_friend_shows(self, user_friends):
        public_lsts = Lst.objects.filter(is_private=False)
        activities = LstSaveActivity.objects.filter(lst__in=public_lsts, saved_by__in=user_friends)
        friend_shows = activities.values_list("show", flat=True).distinct()[:10]
        return friend_shows

    def get_friend_lsts(self, user_friends):
        public_lsts = Lst.objects.filter(is_private=False, is_saved=False, is_watch_later=False)
        friend_lsts = public_lsts.filter(owner__in=user_friends)[:10]
        return friend_lsts

    def get_trending_lsts(self):
        trending_lsts = local_cache.get(("trending_lsts"))
        if not trending_lsts:
            public_lsts = Lst.objects.filter(is_private=False, is_saved=False, is_watch_later=False)
            trending_lsts = public_lsts.order_by("-num_likes")[:20]
            local_cache.set(("trending_lsts"), trending_lsts)

        return trending_lsts

    def get_friend_comments(self, user_friends):
        comments = Comment.objects.filter(owner__in=user_friends).order_by("-created_at")[:10]
        return comments

    def get(self, request, *args, **kwargs):
        user = request.user
        if Discover.objects.filter(user=user):
            user_discover = Discover.objects.get(user=user)
            utc = pytz.utc
            delta = datetime.datetime.now(tz=utc) - user_discover.updated_at
            minutes = (delta.total_seconds() % 3600) // 60
            if minutes < 15:
                seralizer = DiscoverSerializer(user_discover, context={"request": request})
                return success_response(seralizer.data)
        else:
            user_discover = Discover()
            user_discover.user = user
            user_discover.save()

        user_friends = [Profile.objects.get(user=friend) for friend in Friend.objects.friends(user=user)]
        user_discover.friend_recommendations.set(user_friends)
        user_discover.friend_shows.set(self.get_friend_shows(user_friends))
        user_discover.trending_shows.set(self.get_trending_shows())
        user_discover.friend_comments.set(self.get_friend_comments(user_friends))
        user_discover.trending_lsts.set(self.get_trending_lsts())
        user_discover.friend_lsts.set(self.get_friend_lsts(user_friends))
        user_discover.save()

        serializer = DiscoverSerializer(user_discover, context={"request": request})
        return success_response(serializer.data)
