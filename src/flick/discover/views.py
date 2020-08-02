from api.utils import success_response
from django.core.cache import caches
from rest_framework.views import APIView
from show.show_api_utils import ShowAPI
from tag.models import Tag
from tag.serializers import TagSerializer


local_cache = caches["local"]


class DiscoverShow(APIView):
    shows = []

    def get_top_shows_by_type(self, show_type):
        top_shows = local_cache.get(("top", show_type))
        if not top_shows:
            top_shows = ShowAPI.get_top_show_info(show_type)
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
            ext_api_genre_id = tag_data.get("ext_api_genre_id")
            top_shows = ShowAPI.get_top_show_info_by_genre(show_type, ext_api_genre_id)
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
        serializer_data.extend(ShowAPI.create_show_objects(self.shows))

        return success_response(serializer_data)
