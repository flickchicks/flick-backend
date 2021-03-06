from user.user_simple_serializers import UserSimpleSerializer

from api import settings as api_settings
from api.utils import success_response_with_query
from django.contrib.auth.models import User
from django.core.cache import caches
from django.db.models import Q
from lst.models import Lst
from lst.serializers import LstSerializer
from rest_framework.views import APIView
from show.models import Show
from show.serializers import ShowSerializer
from show.show_api_utils import ShowAPI
from tag.models import Tag
from tag.simple_serializers import TagSimpleSerializer


# cache to store search_movie_by_name (and tv and anime)
# search_movie_by_name example: ("query", "movie"), movie_id
local_cache = caches["local"]


class Search(APIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS
    shows = []
    known_shows = []
    request = None
    source = None
    show_type = None

    def get_ext_api_tags_by_tag_ids(self, tag_lst):
        return list(Tag.objects.filter(id__in=tag_lst).values_list("ext_api_genre_id", flat=True))

    def get_show_info(self, show_id):
        known_show = Show.objects.filter(ext_api_id=show_id, ext_api_source=self.source)
        if known_show.exists():
            known_show = Show.objects.get(ext_api_id=show_id, ext_api_source=self.source)
            self.known_shows.append(ShowSerializer(known_show, context={"request": self.request}).data)
        else:
            show = ShowAPI.get_show_info_from_id(self.show_type, show_id)
            if show:
                self.shows.append(show)

    # show_type can be "movie", "tv", "anime"
    def get_shows_by_type_and_query(self, query, show_type, source, page=1, tags=[]):
        self.source = source
        self.show_type = show_type
        shows = local_cache.get((query, show_type, page, tags))
        if not shows:
            ext_api_tags = self.get_ext_api_tags_by_tag_ids(tags)
            shows = ShowAPI.search_shows_by_name(show_type=show_type, name=query, page=page, tags=ext_api_tags)
            local_cache.set((query, show_type, tags), shows)
        self.shows.extend(shows)

    def get_shows_by_query(self, query, is_movie, is_tv, is_multi, is_anime, page=1, tags=[]):
        if is_multi:
            self.get_shows_by_type_and_query(query, "multi", "tmdb", page, tags)
            return
        if is_movie:
            self.get_shows_by_type_and_query(query, "movie", "tmdb", page, tags)
        if is_tv:
            self.get_shows_by_type_and_query(query, "tv", "tmdb", page, tags)
        if is_anime:
            self.get_shows_by_type_and_query(query, "anime", "animelist")

    def get_users_by_username(self, query):
        non_superusers = User.objects.filter(Q(is_superuser=False))
        users = non_superusers.filter(Q(first_name__icontains=query) | Q(username__icontains=query))
        serializer = UserSimpleSerializer(instance=users, many=True, context={"request": self.request})
        return serializer.data

    def get_lsts_by_name(self, query):
        lsts = Lst.objects.filter(
            Q(name__icontains=query) & Q(is_private=False) & Q(is_saved=False) & Q(is_watch_later=False)
        ).prefetch_related("collaborators", "shows", "custom_tags")
        serializer = LstSerializer(lsts, many=True, context={"request": self.request})
        return serializer.data

    def get_tags_by_name(self, query):
        tags = Tag.objects.filter(name__icontains=query)
        return TagSimpleSerializer(tags, many=True).data

    def get(self, request, *args, **kwargs):
        self.request = request
        query = request.query_params.get("query")
        page = request.query_params.get("page", 1)
        tags = request.query_params.getlist("tags", [])
        is_anime = bool(request.query_params.get("is_anime", False))
        is_movie = bool(request.query_params.get("is_movie", False))
        is_tv = bool(request.query_params.get("is_tv", False))
        is_user = bool(request.query_params.get("is_user", False))
        is_lst = bool(request.query_params.get("is_lst", False))
        is_tag = bool(request.query_params.get("is_tag", False))
        is_multi = bool(request.query_params.get("is_multi", False))

        self.shows = []
        self.known_shows = []

        if is_user:
            return success_response_with_query(query=query, data=self.get_users_by_username(query))
        elif is_lst:
            return success_response_with_query(query=query, data=self.get_lsts_by_name(query))
        elif is_tag:
            return success_response_with_query(query=query, data=self.get_tags_by_name(query))
        else:
            self.get_shows_by_query(query, is_movie, is_tv, is_multi, is_anime, page, tags)

        serializer_data = []
        serializer_data.extend(ShowAPI.create_show_objects(self.shows))
        serializer_data.extend(self.known_shows)

        return success_response_with_query(query=query, data=serializer_data)
