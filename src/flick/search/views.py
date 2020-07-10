import datetime
import json

from api import settings as api_settings
from api.utils import failure_response, success_response
from django.contrib.auth.models import User
from django.core.cache import caches
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from lst.models import Lst
from lst.serializers import LstSerializer
from show.models import Show
from show.serializers import ShowSerializer
from show.utils import API
from tag.models import Tag
from user.user_simple_serializers import UserSimpleSerializer


# cache to store get_top_movie and search_movie_by_name (and tv and anime)
# get_top_movie example: ("top", "movie"), movie_id
# search_movie_by_name example: ("query", "movie"), movie_id
local_cache = caches["local"]


class Search(APIView):
    shows = []
    known_shows = []

    # show_type can be "movie", "tv", "anime"
    def get_shows_by_type_and_query(self, query, show_type, source):
        show_ids = local_cache.get((query, show_type))
        if not show_ids:
            show_ids = API.search_show_ids_by_name(show_type, query)
            local_cache.set((query, show_type), show_ids)
        for show_id in show_ids:
            known_show = Show.objects.filter(ext_api_id=show_id, ext_api_source=source)
            if known_show.exists():
                known_show = Show.objects.get(ext_api_id=show_id, ext_api_source=source)
                self.known_shows.append(ShowSerializer(known_show).data)
            else:
                show = API.get_show_info_from_id(show_type, show_id)
                if show:
                    self.shows.append(show)

    def get_shows_by_query(self, query, is_movie, is_tv, is_anime):
        if is_movie:
            self.get_shows_by_type_and_query(query, "movie", "tmdb")
        if is_tv:
            self.get_shows_by_type_and_query(query, "tv", "tmdb")
        if is_anime:
            self.get_shows_by_type_and_query(query, "anime", "animelist")

    def get_top_shows_by_type(self, show_type):
        top_shows = local_cache.get(("top", show_type))
        if not top_shows:
            top_shows = API.get_top_show_info(show_type)
            local_cache.set(("top", show_type), top_shows)
        self.shows.extend(top_shows)

    def get_top_shows(self, is_movie, is_tv, is_anime):
        if is_movie:
            self.get_top_shows_by_type("movie")
        if is_tv:
            self.get_top_shows_by_type("tv")
        if is_anime:
            self.get_top_shows_by_type("anime")

    def get_users_by_username(self, query):
        users = User.objects.filter(username__icontains=query)
        serializer = UserSimpleSerializer(users, many=True)
        return serializer.data

    def get_lists_by_name(self, query):
        lists = Lst.objects.filter(lst_name__icontains=query)
        serializer = LstSerializer(lists, many=True)
        return serializer.data

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query")
        print(f"query: {query}")
        is_anime = bool(request.query_params.get("is_anime", False))
        print(f"is_anime: {is_anime}")
        is_movie = bool(request.query_params.get("is_movie", False))
        print(f"is_movie: {is_movie}")
        is_tv = bool(request.query_params.get("is_tv", False))
        print(f"is_tv: {is_tv}")
        is_top = bool(request.query_params.get("is_top", False))
        print(f"is_top: {is_top}")
        is_user = bool(request.query_params.get("is_user", False))
        print(f"is_user: {is_user}")
        is_list = bool(request.query_params.get("is_list", False))
        print(f"is_: {is_list}")

        self.shows = []
        self.known_shows = []

        if is_user:
            return success_response(self.get_users_by_username(query))
        elif is_list:
            return success_response(self.get_lists_by_name(query))
        elif is_top:
            self.get_top_shows(is_movie, is_tv, is_anime)
        else:
            self.get_shows_by_query(query, is_movie, is_tv, is_anime)

        serializer_data = []
        serializer_data.extend(API.create_show_objects(self.shows))
        serializer_data.extend(self.known_shows)

        return success_response(serializer_data)
