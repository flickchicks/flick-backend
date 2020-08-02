import pprint as pp

from flick.tasks import populate_show_details
import tmdbsimple as tmdb

from .animelist_api_utils import AnimeList_API
from .models import Show
from .serializers import ShowSearchSerializer
from .tmdb_api_utils import TMDB_API


class API:
    @staticmethod
    def create_show_objects(request, show_info_lst):
        serializer_data = []
        for show_info in show_info_lst:
            if not show_info:
                continue
            if Show.objects.filter(
                title=show_info.get("title"),
                ext_api_id=show_info.get("ext_api_id"),
                ext_api_source=show_info.get("ext_api_source"),
            ):
                show = Show.objects.get(
                    title=show_info.get("title"),
                    ext_api_id=show_info.get("ext_api_id"),
                    ext_api_source=show_info.get("ext_api_source"),
                )
                serializer = ShowSearchSerializer(show)
                serializer_data.append(serializer.data)
            else:
                try:
                    show = Show()
                    show.title = show_info.get("title")
                    show.ext_api_id = show_info.get("ext_api_id")
                    show.ext_api_source = show_info.get("ext_api_source")
                    show.poster_pic = show_info.get("poster_pic")
                    show.is_tv = show_info.get("is_tv")
                    show.plot = show_info.get("plot")
                    show.date_released = show_info.get("date_released")
                    show.status = show_info.get("status")
                    show.language = show_info.get("language")
                    show.duration = show_info.get("duration")
                    show.seasons = show_info.get("seasons")
                    show.save()
                    populate_show_details.delay(show.id)
                    serializer = ShowSearchSerializer(show)
                    serializer_data.append(serializer.data)
                except Exception as e:
                    print("here", e)
        return serializer_data

    @staticmethod
    def get_top_show_info(show_type):
        if show_type == "movie":
            api = TMDB_API()
            return api.get_top_movie()
        elif show_type == "tv":
            api = TMDB_API()
            return api.get_top_tv()
        elif show_type == "anime":
            api = AnimeList_API()
            return api.get_top_anime()
        return None

    @staticmethod
    def search_shows_by_name(show_type, name, tags=[]):
        """
        show_type can be 'movie', 'tv', or 'anime'
        """
        if show_type == "movie":
            api = TMDB_API()
            return api.search_movie_by_name(name, tags)
        elif show_type == "tv":
            api = TMDB_API()
            return api.search_tv_by_name(name, tags)
        elif show_type == "anime":
            api = AnimeList_API()
            return api.search_anime_by_name(name)
        return None

    @staticmethod
    def get_show_info_from_id(show_type, id):
        if show_type == "movie":
            api = TMDB_API()
            return api.get_movie_info_from_id(id)
        elif show_type == "tv":
            api = TMDB_API()
            return api.get_tv_info_from_id(id)
        elif show_type == "anime":
            api = AnimeList_API()
            return api.get_anime_info_from_id(id)
        print("only movie, tv, and anime show types are supported!")
        return None

    @staticmethod
    def get_top_show_info_by_genre(show_type, tag_id):
        if show_type == "movie":
            api = TMDB_API()
            return api.discover_movies_by_genre(tag_id)
        elif show_type == "tv":
            api = TMDB_API()
            return api.discover_tvs_by_genre(tag_id)
        elif show_type == "anime":
            api = AnimeList_API()
            return api.get_top_anime()
        return None
