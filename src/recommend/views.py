from random import sample

from api import settings as api_settings
from api.utils import success_response
from django.core.cache import caches
from lst.models import Lst
from rest_framework import generics
from show.show_api_utils import ShowAPI
from show.simple_serializers import ShowSimpleSerializer
from show.tmdb import flicktmdb

local_cache = caches["local"]


class LstRecommendView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS
    api = flicktmdb()

    def get(self, request, pk):
        lst = Lst.objects.get(pk=pk)
        shows = lst.shows.filter(ext_api_source="tmdb")
        show_ids = set(shows.values_list("ext_api_id", flat=True))

        rec_shows = []
        for show in shows:
            similar = local_cache.get((show.id, "similar"))
            if not similar:
                similar = self.api.get_similar_shows(show.ext_api_id, show.is_tv)
                local_cache.set((show.id, "similar"), similar)
            similar = filter(lambda a: a.get("ext_api_id") not in show_ids, similar)
            rec_shows.extend(similar)

        data = ShowAPI.create_show_objects(rec_shows, serializer=ShowSimpleSerializer)
        serializer_data = sample(data, min(15, len(data)))
        return success_response(serializer_data)
