from random import sample

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.core.cache import caches
from lst.models import Lst
from rest_framework import generics
from show.show_api_utils import ShowAPI
from show.simple_serializers import ShowSimpleSerializer
from show.tmdb import flicktmdb

local_cache = caches["local"]


# Create your views here.
class LstRecommendView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        """
        Get a specific list by id.
        If the request user is a collaborator or an owner or is looking at a list that is public,
        then the list will be returned.
        """
        if not Lst.objects.filter(pk=pk):
            return failure_response(f"List of id {pk} does not exist.")
        lst = Lst.objects.get(pk=pk)
        shows = lst.shows.filter(ext_api_source="tmdb")

        rec_shows = []
        for show in shows:
            similar = local_cache.get((show.id, "similar"))
            if not similar:
                similar = flicktmdb().get_similar_shows(show.ext_api_id, show.is_tv)
            rec_shows.extend(similar)

        data = ShowAPI.create_show_objects(rec_shows, serializer=ShowSimpleSerializer)
        try:
            serializer_data = sample(data, 15)
        except:
            serializer_data = data
        return success_response(serializer_data)
