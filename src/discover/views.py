from api.utils import success_response
from django.core.cache import caches
from rest_framework.views import APIView
from show.show_api_utils import ShowAPI
from show.simple_serializers import ShowSimplestSerializer
from tag.models import Tag
from tag.serializers import TagSerializer


local_cache = caches["local"]


class DiscoverShow(APIView):
    def get_shows_by_type(self, show_type, search_type, search_fn):
        shows = local_cache.get((search_type, show_type))
        if not shows:
            shows = search_fn(show_type)
            local_cache.set((search_type, show_type), shows)
        return shows

    def get_top_shows(self, is_movie, is_tv, is_anime):
        if is_movie:
            movies = self.get_shows_by_type("movie", "top", ShowAPI.get_top_show_info)
        if is_tv:
            tvs = self.get_shows_by_type("tv", "top", ShowAPI.get_top_show_info)
        if is_anime:
            animes = self.get_shows_by_type("anime", "top", ShowAPI.get_top_show_info)
        return movies, tvs, animes

    def get_popular_shows(self, is_movie, is_tv, is_anime):
        if is_movie:
            movies = self.get_shows_by_type("movie", "popular", ShowAPI.get_popular_show_info)[:5]
        if is_tv:
            tvs = self.get_shows_by_type("tv", "popular", ShowAPI.get_popular_show_info)[:5]
        if is_anime:
            animes = self.get_shows_by_type("anime", "popular", ShowAPI.get_popular_show_info)[:5]
        return movies, tvs, animes

    def get_now_playing_shows(self, is_movie, is_tv, is_anime):
        if is_movie:
            movies = self.get_shows_by_type("movie", "now_playing", ShowAPI.get_now_playing_show_info)
        if is_tv:
            tvs = self.get_shows_by_type("tv", "now_playing", ShowAPI.get_now_playing_show_info)
        if is_anime:
            animes = self.get_shows_by_type("anime", "now_playing", ShowAPI.get_now_playing_show_info)
        return movies, tvs, animes

    def get_top_shows_by_type_and_genre(self, show_type, tag_id):
        top_shows = local_cache.get(("top", show_type, tag_id))
        if not top_shows:
            tag_data = TagSerializer(Tag.objects.get(id=tag_id)).data
            ext_api_genre_id = tag_data.get("ext_api_genre_id")
            top_shows = ShowAPI.get_top_show_info_by_genre(show_type, ext_api_genre_id)
            local_cache.set(("top", show_type, tag_id), top_shows)
        return top_shows

    def get_top_shows_by_genre(self, is_movie, is_tv, is_anime, tag_id):
        if is_movie:
            movies = self.get_top_shows_by_type_and_genre("movie", tag_id)
        if is_tv:
            tvs = self.get_top_shows_by_type_and_genre("tv", tag_id)
        if is_anime:
            animes = self.get_shows_by_type(
                "anime", "top", ShowAPI.get_top_show_info
            )  # genre does not seem to be fully integrated in the anime api
        return movies, tvs, animes

    def get(self, request, *args, **kwargs):
        # tag_id = request.query_params.get("tag_id", "")
        # print(f"genre: {tag_id}")
        # is_anime = bool(request.query_params.get("is_anime", False))
        # print(f"is_anime: {is_anime}")
        # is_movie = bool(request.query_params.get("is_movie", False))
        # print(f"is_movie: {is_movie}")
        # is_tv = bool(request.query_params.get("is_tv", False))
        # print(f"is_tv: {is_tv}")
        # is_top = bool(request.query_params.get("is_top", False))
        # print(f"is_top: {is_top}")
        # is_now = bool(request.query_params.get("is_now", False))
        # print(f"is_now: {is_now}")
        # is_popular = bool(request.query_params.get("is_popular", False))
        # print(f"is_popular: {is_popular}")

        # self.shows = []

        # if tag_id:
        #     self.get_top_shows_by_genre(is_movie, is_tv, is_anime, tag_id)
        # elif is_now:
        #     self.get_now_playing_shows(is_movie, is_tv, is_anime)
        # elif is_popular:
        #     self.get_popular_shows(is_movie, is_tv, is_anime)
        # elif is_top:
        #     self.get_top_shows(is_movie, is_tv, is_anime)

        movies, tvs, animes = self.get_popular_shows(True, True, True)
        serializer_data = dict()
        serializer_data["trending_movies"] = ShowAPI.create_show_objects(movies, ShowSimplestSerializer)
        serializer_data["trending_tvs"] = ShowAPI.create_show_objects(tvs, ShowSimplestSerializer)
        serializer_data["trending_animes"] = ShowAPI.create_show_objects(animes, ShowSimplestSerializer)

        return success_response(serializer_data)
