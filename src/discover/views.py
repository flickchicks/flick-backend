import datetime
from user.models import Profile

from api import settings as api_settings
from api.utils import success_response
from comment.models import Comment
from discover_recommend.models import DiscoverRecommendation
from django.core.cache import caches
from friendship.models import Friend
from lst.models import Lst
import pytz
from rest_framework.views import APIView
from show.models import Show
from show.show_api_utils import ShowAPI
from show.simple_serializers import ShowSimplestSerializer
from show.tmdb import flicktmdb

from .models import Discover
from .serializers import DiscoverSerializer

local_cache = caches["local"]


class DiscoverShow(APIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS
    api = flicktmdb()

    def get_friend_recommendations(self, user):
        pass

    def get_show_recommendations(self, user):
        trending = local_cache.get(("trending"))
        if not trending:
            trending = self.api.get_trending_shows()
            local_cache.set(("trending"), trending)
        shows = ShowAPI.create_show_objects(trending, ShowSimplestSerializer)
        show_recs = []
        for show in shows:
            show = Show.objects.get(id=show["id"])
            if DiscoverRecommendation.objects.filter(show=show, recommend_type="trending_show"):
                discover_rec = DiscoverRecommendation.objects.get(show=show, recommend_type="trending_show")
            else:
                discover_rec = DiscoverRecommendation()
                discover_rec.recommend_type = "trending_show"
                discover_rec.show = show
                discover_rec.save()
            show_recs.append(discover_rec)
        return show_recs

    def get_list_recommendations(self, user):
        public_lsts = Lst.objects.filter(is_private=False, is_saved=False, is_watch_later=False)
        lst_recs = []
        lsts = set()

        friends = [Profile.objects.get(user=friend) for friend in Friend.objects.friends(user=user)]
        friend_lsts = list(public_lsts.filter(owner__in=friends))[:10]
        for lst in friend_lsts:
            if DiscoverRecommendation.objects.filter(lst=lst, recommend_type="friend_list"):
                discover_rec = DiscoverRecommendation.objects.get(lst=lst, recommend_type="friend_list")
            else:
                discover_rec = DiscoverRecommendation()
                discover_rec.recommend_type = "friend_list"
                discover_rec.lst = lst
                discover_rec.save()
            lst_recs.append(discover_rec)
            lsts.add(lst)

        popular_lsts = sorted(list(public_lsts), key=lambda x: x.num_likes, reverse=True)[:10]
        for lst in popular_lsts:
            if lst in lsts:
                continue
            if DiscoverRecommendation.objects.filter(lst=lst, recommend_type="trending_list"):
                discover_rec = DiscoverRecommendation.objects.get(lst=lst, recommend_type="trending_list")
            else:
                discover_rec = DiscoverRecommendation()
                discover_rec.recommend_type = "trending_list"
                discover_rec.lst = lst
                discover_rec.save()
            lst_recs.append(discover_rec)
            lsts.add(lst)

        return lst_recs

    def get_friend_comments(self, user):
        friends = [Profile.objects.get(user=friend) for friend in Friend.objects.friends(user=user)]
        comments = list(Comment.objects.filter(owner__in=friends))[-10:]
        return comments[::-1]

    def get(self, request, *args, **kwargs):
        user = request.user
        if Discover.objects.filter(user=user):
            user_discover = Discover.objects.get(user=user)
            utc = pytz.utc
            delta = datetime.datetime.now(tz=utc) - user_discover.updated_at
            minutes = (delta.total_seconds() % 3600) // 60
            if minutes < 30:
                seralizer = DiscoverSerializer(user_discover)
                return success_response(seralizer.data)
        else:
            user_discover = Discover()
            user_discover.user = user
            user_discover.save()

        user_friends = [Profile.objects.get(user=friend) for friend in Friend.objects.friends(user=user)]
        user_discover.friend_recommendations.set(user_friends)
        user_discover.show_recommendations.set(self.get_show_recommendations(user))
        user_discover.friend_comments.set(self.get_friend_comments(user))
        user_discover.list_recommendations.set(self.get_list_recommendations(user))
        user_discover.save()

        seralizer = DiscoverSerializer(user_discover)
        return success_response(seralizer.data)
