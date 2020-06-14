import datetime
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
from tag.models import Tag


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

        known_shows = []

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
                print("is movie")
                movie_ids = TMDB_API.search_movie_by_name(query)
                for movie_id in movie_ids:
                    known_show = Show.objects.filter(ext_api_id=movie_id, ext_api_source="tmdb", is_tv=False)
                    if not known_show.exists():
                        shows.append(TMDB_API.get_movie_info_from_id(movie_id))
                    else:
                        known_show = Show.objects.get(ext_api_id=movie_id, ext_api_source="tmdb", is_tv=False)
                        known_shows.append(ShowSerializer(known_show).data)
            if is_tv:
                print("is tv")
                tv_ids = TMDB_API.search_tv_by_name(query)
                for tv_id in tv_ids:
                    known_show = Show.objects.filter(ext_api_id=tv_id, ext_api_source="tmdb", is_tv=True)
                    if not known_show.exists():
                        shows.append(TMDB_API.get_movie_info_from_id(tv_id))
                    else:
                        known_show = Show.objects.get(ext_api_id=movie_id, ext_api_source="tmdb", is_tv=True)
                        known_shows.append(ShowSerializer(known_show).data)
            if is_anime:
                anime_ids = AnimeList_API.search_anime_by_keyword(query)
                anime_info = [AnimeList_API.search_anime_by_id(id) for id in anime_ids]
                shows += anime_info

        serializer_data = []

        # print(f"known_shows {known_shows}")

        # print(f"shows {shows}")
        for search_result in shows:
            if not search_result:
                continue
            try:
                show = Show()
                show.title = search_result.get("title")
                show.ext_api_id = search_result.get("ext_api_id")
                show.ext_api_source = search_result.get("ext_api_source")
                show.poster_pic = search_result.get("poster_pic")
                show.is_tv = search_result.get("is_tv")
                show.date_released = search_result.get("date_released")
                show.status = search_result.get("status")
                show.language = search_result.get("language")
                show.duration = search_result.get("duration")
                show.plot = search_result.get("plot")
                show.seasons = search_result.get("seasons")
                show.save()
                for tag_name in search_result.get("show_tags"):
                    print("tag_name {tag_name}")
                    show.tags.create(tag=tag_name)
                show.save()
                serializer = ShowSerializer(show)
                serializer_data.append(serializer.data)
            except:  # Exception as e:
                print("ignore")
                # print(f"{e}: {search_result}")
        for show in known_shows:
            serializer_data.append(show)

        print(f"known shows {known_shows}")

        return success_response(serializer_data)
