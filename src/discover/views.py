from user.models import Profile

from api import settings as api_settings
from api.utils import success_response
from discover_recommend.models import DiscoverRecommendation
from django.contrib.auth.models import User
from django.core.cache import caches
from friendship.models import Friend
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
        trending = self.api.get_trending_shows()
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
                discover_rec.lst = None
                discover_rec.save()
            show_recs.append(discover_rec)
        return show_recs

    def get_list_recommendations(self, user):
        pass

    def get_friend_comments(self, user):
        pass

    def get(self, request, *args, **kwargs):
        if Discover.objects.filter(user=request.user):
            user_discover = Discover.objects.get(user=request.user)
            # check update at
        else:
            user_discover = Discover()
            user_discover.user = request.user
        for show in self.get_show_recommendations(request.user):
            user_discover.show_recommendations.add(show)

        user_friends = [User.objects.get(id=friend.id) for friend in Friend.objects.friends(user=request.user)]
        for friend in user_friends:
            user_discover.friend_recommendations.add(Profile.objects.get(user=friend))
        user_discover.save()

        seralizer = DiscoverSerializer(user_discover)
        return success_response(seralizer.data)
