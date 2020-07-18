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
from tag.serializers import TagSerializer
from user.user_simple_serializers import UserSimpleSerializer


local_cache = caches["local"]


class DiscoverShow(APIView):
    shows = []

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

    def get_top_shows_by_type_and_genre(self, show_type, tag_id):
        top_shows = local_cache.get(("top", show_type, tag_id))
        if not top_shows:
            tag_data = TagSerializer(Tag.objects.get(id=tag_id)).data
            ext_api_tag = tag_data.get("ext_api_id")
            top_shows = API.get_top_show_info_by_genre(show_type, ext_api_tag)
            local_cache.set(("top", show_type, tag_id), top_shows)
        self.shows.extend(top_shows)

    def get_top_shows_by_genre(self, is_movie, is_tv, is_anime, tag_id):
        if is_movie:
            self.get_top_shows_by_type_and_genre("movie", tag_id)
        if is_tv:
            self.get_top_shows_by_type_and_genre("tv", tag_id)
        if is_anime:
            self.get_top_shows_by_type("anime")  # genre does not seem to be fully integrated in the anime api

    def get(self, request, *args, **kwargs):
        tag_id = request.query_params.get("tag_id", "")
        print(f"genre: {tag_id}")
        is_anime = bool(request.query_params.get("is_anime", False))
        print(f"is_anime: {is_anime}")
        is_movie = bool(request.query_params.get("is_movie", False))
        print(f"is_movie: {is_movie}")
        is_tv = bool(request.query_params.get("is_tv", False))
        print(f"is_tv: {is_tv}")

        self.shows = []

        if tag_id:
            self.get_top_shows_by_genre(is_movie, is_tv, is_anime, tag_id)
        else:
            self.get_top_shows(is_movie, is_tv, is_anime)

        serializer_data = []
        serializer_data.extend(API.create_show_objects(self.shows))

        return success_response(serializer_data)
