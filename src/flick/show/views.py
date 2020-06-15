import datetime
import json

from api import settings as api_settings
from api.utils import failure_response, success_response
from django.core.cache import caches
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Show
from .serializers import ShowSerializer
from .utils import TMDB_API, AnimeList_API, create_show_objects
from tag.models import Tag

local_cache = caches["local"]


class ShowViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Show: see all shows, get a specific show
    """

    queryset = Show.objects.all()
    serializer_class = ShowSerializer

    # if api_settings.UNPROTECTED, then any user can see this
    permission_classes = api_settings.STANDARD_PERMISSIONS

    # don't need this, generics has this code, but this overrides
    # gives option to add additional checks / customize
    # def list(self, request):
    #     # can access logged in user via request.user
    #     self.serializer_class = ShowSerializer
    #     return super(ItemList, self).list(request)

    # def retrieve(self, request, pk):
    #     queryset = self.get_object()
    #     serializer = ShowDetailSerializer(queryset, many=False)
    #     return success_response(serializer.data)


class SearchShow(APIView):
    permission_classes = api_settings.UNPROTECTED

    # cache to store get_top_movie and search_movie_by_name (and tv and anime)
    # get_top_movie example: ("top", "movie"), movie_id
    # search_movie_by_name example: ("query", "movie"), movie_id

    def get_top(self, shows, is_movie, is_tv, is_anime):
        if is_movie:
            top_movies = local_cache.get(("top", "movie"))
            if not top_movies:
                top_movies = TMDB_API.get_top_movie()
                local_cache.set(("top", "movie"), top_movies)
            shows += top_movies if top_movies else []
        if is_tv:
            top_shows = local_cache.get(("top", "shows"))
            if not top_shows:
                top_shows = TMDB_API.get_top_tv()
                local_cache.set(("top", "shows"), top_shows)
            shows += top_shows if top_shows else []
        if is_anime:
            top_anime = local_cache.get(("top", "anime"))
            if not top_anime:
                top_anime = AnimeList_API.get_top_anime()
                local_cache.set(("top", "anime"), top_anime)
            shows += top_anime if top_anime else []

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query")
        print(f"query: {query}")
        is_anime = bool(request.query_params.get("is_anime"))
        print(f"is_anime: {is_anime}")
        is_movie = bool(request.query_params.get("is_movie"))
        print(f"is_movie: {is_movie}")
        is_tv = bool(request.query_params.get("is_tv"))
        print(f"is_tv: {is_tv}")
        is_top = bool(request.query_params.get("is_top"))
        print(f"is_top: {is_top}")

        shows = []
        known_shows = []

        if is_top:
            self.get_top(shows, is_movie, is_tv, is_anime)

        else:
            if is_movie:
                movie_ids = local_cache.get((query, "movie"))
                if not movie_ids:
                    movie_ids = TMDB_API.search_movie_by_name(query)
                    local_cache.set((query, "movie"), movie_ids)
                for movie_id in movie_ids:
                    known_show = Show.objects.filter(ext_api_id=movie_id, ext_api_source="tmdb")
                    if known_show.exists():
                        known_show = Show.objects.get(ext_api_id=movie_id, ext_api_source="tmdb")
                        known_shows.append(ShowSerializer(known_show).data)
                    else:
                        show = TMDB_API.get_movie_info_from_id(movie_id)
                        if show:
                            shows.append(show)

            if is_tv:
                tv_ids = local_cache.get((query, "tv"))
                if not tv_ids:
                    tv_ids = TMDB_API.search_tv_by_name(query)
                    local_cache.set((query, "tv"), tv_ids)
                for tv_id in tv_ids:
                    known_show = Show.objects.filter(ext_api_id=tv_id, ext_api_source="tmdb")
                    if known_show.exists():
                        known_show = Show.objects.get(ext_api_id=tv_id, ext_api_source="tmdb")
                        known_shows.append(ShowSerializer(known_show).data)
                    else:
                        show = TMDB_API.get_movie_info_from_id(tv_id)
                        if show:
                            shows.append(show)

            if is_anime:
                anime_ids = local_cache.get((query, "anime"))
                if not anime_ids:
                    anime_ids = AnimeList_API.search_anime_by_keyword(query)
                    local_cache.set((query, "anime"), anime_ids)
                for anime_id in anime_ids:
                    known_show = Show.objects.filter(ext_api_id=anime_id, ext_api_source="animelist")
                    if known_show.exists():
                        known_show = Show.objects.get(ext_api_id=anime_id, ext_api_source="animelist")
                        known_shows.append(ShowSerializer(known_show).data)
                    else:
                        show = AnimeList_API.search_anime_by_id(anime_id)
                        if show:
                            shows.append(show)

        serializer_data = []

        serializer_data.extend(create_show_objects(shows))

        serializer_data.extend(known_shows)

        return success_response(serializer_data)
