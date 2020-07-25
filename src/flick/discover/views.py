from api.utils import success_response
from django.core.cache import caches
from rest_framework.views import APIView
from show.utils import API
from tag.models import Tag
from tag.serializers import TagSerializer


local_cache = caches["local"]


class DiscoverShow(APIView):
    shows = []

    def get_shows_by_type(self, show_type, search_type, search_fn):
        shows = local_cache.get((search_type, show_type))
        if not shows:
            shows = search_fn(show_type)
            local_cache.set((search_type, show_type), shows)
        self.shows.extend(shows)

    def get_top_shows(self, is_movie, is_tv, is_anime):
        if is_movie:
            self.get_shows_by_type("movie", "top", API.get_top_show_info)
        if is_tv:
            self.get_shows_by_type("tv", "top", API.get_top_show_info)
        if is_anime:
            self.get_shows_by_type("anime", "top", API.get_top_show_info)

    def get_popular_shows(self, is_movie, is_tv, is_anime):
        if is_movie:
            self.get_shows_by_type("movie", "popular", API.get_popular_show_info)
        if is_tv:
            self.get_shows_by_type("tv", "popular", API.get_popular_show_info)
        if is_anime:
            self.get_shows_by_type("anime", "popular", API.get_popular_show_info)

    def get_now_playing_shows(self, is_movie, is_tv, is_anime):
        if is_movie:
            self.get_shows_by_type("movie", "now_playing", API.get_now_playing_show_info)
        if is_tv:
            self.get_shows_by_type("tv", "now_playing", API.get_now_playing_show_info)
        if is_anime:
            self.get_shows_by_type("anime", "now_playing", API.get_now_playing_show_info)

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
            self.get_top_shows("anime")  # genre does not seem to be fully integrated in the anime api

    def get(self, request, *args, **kwargs):
        tag_id = request.query_params.get("tag_id", "")
        print(f"genre: {tag_id}")
        is_anime = bool(request.query_params.get("is_anime", False))
        print(f"is_anime: {is_anime}")
        is_movie = bool(request.query_params.get("is_movie", False))
        print(f"is_movie: {is_movie}")
        is_tv = bool(request.query_params.get("is_tv", False))
        print(f"is_tv: {is_tv}")
        is_top = bool(request.query_params.get("is_top", False))
        print(f"is_top: {is_top}")
        is_now = bool(request.query_params.get("is_now", False))
        print(f"is_now: {is_now}")
        is_popular = bool(request.query_params.get("is_popular", False))
        print(f"is_popular: {is_popular}")

        self.shows = []

        if tag_id:
            self.get_top_shows_by_genre(is_movie, is_tv, is_anime, tag_id)
        elif is_now:
            self.get_now_playing_shows(is_movie, is_tv, is_anime)
        elif is_popular:
            self.get_popular_shows(is_movie, is_tv, is_anime)
        elif is_top:
            self.get_top_shows(is_movie, is_tv, is_anime)

        serializer_data = []
        serializer_data.extend(API.create_show_objects(self.shows))

        return success_response(serializer_data)
