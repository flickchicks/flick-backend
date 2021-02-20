from user.models import Profile

from api import settings as api_settings
from api.utils import success_response
from django.contrib.auth.models import User
from django.core.cache import caches
from friendship.models import Friend
from rest_framework.views import APIView

from .models import Discover
from .serializers import DiscoverSerializer


local_cache = caches["local"]


class DiscoverShow(APIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get_friend_recommendations(self, user):
        pass

    def get_show_recommendations(self, user):
        pass

    def get_list_recommendations(self, user):
        pass

    def get_friend_comments(self, user):
        pass

    def get(self, request, *args, **kwargs):
        user_discover = Discover.objects.get(user=request.user)
        if not user_discover:
            user_discover = Discover()
            user_discover.user = request.user

        user_friends = [User.objects.get(id=friend.id) for friend in Friend.objects.friends(user=request.user)]
        for friend in user_friends:
            user_discover.friend_recommendations.add(Profile.objects.get(user=friend))
        user_discover.save()

        seralizer = DiscoverSerializer(user_discover)
        return success_response(seralizer.data)
