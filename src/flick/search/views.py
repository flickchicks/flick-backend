from multiprocessing.pool import ThreadPool as Pool
from user.user_simple_serializers import UserSimpleSerializer

from api import settings as api_settings
from api.utils import success_response
from django.contrib.auth.models import User
from django.core.cache import caches
from lst.models import Lst
from lst.serializers import LstSerializer
from rest_framework.views import APIView
from show.models import Show
from show.serializers import ShowSerializer
from show.utils import API
from tag.models import Tag
from tag.serializers import TagSerializer

# cache to store search_movie_by_name (and tv and anime)
# search_movie_by_name example: ("query", "movie"), movie_id
local_cache = caches["local"]


class Search(APIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS
    shows = []
    known_shows = []
    request = None
    pool = None
    source = None
    show_type = None

    def get_ext_api_tags_by_tag_ids(self, tag_lst):
        ext_api_tags = []
        for tag_id in tag_lst:
            tag_data = TagSerializer(Tag.objects.get(id=tag_id)).data
            ext_api_tags.append(tag_data.get("ext_api_id"))
        return ext_api_tags

    def get_show_info(self, show_id):
        known_show = Show.objects.filter(ext_api_id=show_id, ext_api_source=self.source)
        if known_show.exists():
            known_show = Show.objects.get(ext_api_id=show_id, ext_api_source=self.source)
            self.known_shows.append(ShowSerializer(known_show, context={"request": self.request}).data)
        else:
            show = API.get_show_info_from_id(self.show_type, show_id)
            if show:
                self.shows.append(show)

    # show_type can be "movie", "tv", "anime"
    def get_shows_by_type_and_query(self, query, show_type, source, tags=[]):
        self.source = source
        self.show_type = show_type
        show_ids = local_cache.get((query, show_type, tags))
        if not show_ids:
            ext_api_tags = self.get_ext_api_tags_by_tag_ids(tags)
            show_ids = API.search_show_ids_by_name(show_type, query, ext_api_tags)
            local_cache.set((query, show_type, tags), show_ids)
            self.shows.extend(show_ids)

    def get_shows_by_query(self, query, is_movie, is_tv, is_anime, tags):
        if is_movie:
            self.get_shows_by_type_and_query(query, "movie", "tmdb", tags)
        if is_tv:
            self.get_shows_by_type_and_query(query, "tv", "tmdb", tags)
        if is_anime:
            self.get_shows_by_type_and_query(query, "anime", "animelist")

    def get_users_by_username(self, query):
        users = User.objects.filter(username__icontains=query)
        serializer = UserSimpleSerializer(users, many=True)
        return serializer.data

    def get_lsts_by_name(self, query):
        lsts = Lst.objects.filter(lst_name__icontains=query)
        serializer = LstSerializer(lsts, many=True)
        return serializer.data

    def get(self, request, *args, **kwargs):
        self.request = request
        self.pool = Pool(processes=4)
        query = request.query_params.get("query")
        tags = request.query_params.getlist("tags", [])
        is_anime = bool(request.query_params.get("is_anime", False))
        is_movie = bool(request.query_params.get("is_movie", False))
        is_tv = bool(request.query_params.get("is_tv", False))
        is_user = bool(request.query_params.get("is_user", False))
        is_lst = bool(request.query_params.get("is_lst", False))

        self.shows = []
        self.known_shows = []

        if is_user:
            return success_response(self.get_users_by_username(query))
        elif is_lst:
            return success_response(self.get_lsts_by_name(query))
        else:
            self.get_shows_by_query(query, is_movie, is_tv, is_anime, tags)

        serializer_data = []
        serializer_data.extend(API.create_show_objects(self.request, self.shows))
        serializer_data.extend(self.known_shows)

        return success_response(serializer_data)
