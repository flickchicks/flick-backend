import json

from api import settings as api_settings
from api.utils import failure_response, success_response
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
from .utils import TMDB_API, AnimeList_API


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

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query")
        is_anime = request.query_params.get("is_anime")
        is_movie = request.query_params.get("is_movie")
        is_tv = request.query_params.get("is_tv")
        is_top = request.query_params.get("is_top")

        shows = []

        if is_top:
            if is_movie:
                top_movies = TMDB_API.get_top_movie()
                shows += top_movies if top_movies else []
            if is_tv:
                top_shows = TMDB_API.get_top_tv()
                shows += top_shows if top_shows else []
            if is_anime:
                top_anime = AnimeList_API.get_top_anime()
                shows += top_anime if top_anime else []
        else:
            if is_movie:
                movie_ids = TMDB_API.search_movie_by_name(query)
                movie_info = [TMDB_API.get_movie_info_from_id(id) for id in movie_ids]
                shows += movie_info
            if is_tv:
                tv_ids = TMDB_API.search_tv_by_name(query)
                tv_info = [TMDB_API.get_movie_info_from_id(id) for id in tv_ids]
                shows += tv_info
            if is_anime:
                anime_ids = AnimeList_API.search_anime_by_keyword(query)
                # anime info from search?
                anime_info = [AnimeList_API.search_anime_by_id(id) for id in anime_ids]
                shows += anime_info
        return success_response(shows)
