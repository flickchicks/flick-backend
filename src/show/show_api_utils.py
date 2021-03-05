from flick.tasks import populate_show_details
import tmdbsimple as tmdb

from .animelist import flickanimelist
from .animelist_api_utils import AnimeList_API
from .models import Show
from .serializers import ShowSearchSerializer
from .tmdb import flicktmdb
from .tmdb_api_utils import TMDB_API


class ShowAPI:
    @staticmethod
    def create_show_objects(show_info_lst, serializer=ShowSearchSerializer):
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
                s = serializer(show)
                serializer_data.append(s.data)
            else:
                try:
                    show = Show()
                    show.backdrop_pic = show_info.get("backdrop_pic")
                    show.date_released = show_info.get("date_released")
                    show.ext_api_id = show_info.get("ext_api_id")
                    show.ext_api_source = show_info.get("ext_api_source")
                    show.is_adult = show_info.get("is_adult")
                    show.is_tv = show_info.get("is_tv")
                    show.language = show_info.get("language")
                    show.plot = show_info.get("plot")
                    show.poster_pic = show_info.get("poster_pic")
                    show.title = show_info.get("title")
                    show.save()
                    populate_show_details.delay(show.id)
                    s = serializer(show)
                    serializer_data.append(s.data)
                except Exception as e:
                    print("create_show_objects:", e)
        return serializer_data

    @staticmethod
    def create_show_objects_no_serialization(show_info_lst):
        show_objects = []
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
                show_objects.append(show)
            else:
                try:
                    show = Show()
                    show.backdrop_pic = show_info.get("backdrop_pic")
                    show.date_released = show_info.get("date_released")
                    show.ext_api_id = show_info.get("ext_api_id")
                    show.ext_api_source = show_info.get("ext_api_source")
                    show.is_adult = show_info.get("is_adult")
                    show.is_tv = show_info.get("is_tv")
                    show.language = show_info.get("language")
                    show.plot = show_info.get("plot")
                    show.poster_pic = show_info.get("poster_pic")
                    show.title = show_info.get("title")
                    show.save()
                    populate_show_details.delay(show.id)
                    show_objects.append(show)
                except Exception as e:
                    print("create_show_objects:", e)
        return show_objects

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
    def get_popular_show_info(show_type):
        if show_type == "movie":
            api = TMDB_API()
            return api.get_popular_movie()
        elif show_type == "tv":
            api = TMDB_API()
            return api.get_popular_tv()
        elif show_type == "anime":
            api = AnimeList_API()
            return api.get_top_anime()
        return None

    @staticmethod
    def get_now_playing_show_info(show_type):
        if show_type == "movie":
            api = TMDB_API()
            return api.get_now_playing_movie()
        elif show_type == "tv":
            api = TMDB_API()
            return api.get_now_playing_tv()
        elif show_type == "anime":
            api = AnimeList_API()
            return api.get_top_anime()
        return None

    @staticmethod
    def search_shows_by_name(show_type, name, page=1, tags=[]):
        """
        show_type can be 'movie', 'tv', or 'anime'
        """
        if show_type == "movie":
            return flicktmdb().search_show(query=name, page=page, tags=tags, is_tv=False)
        elif show_type == "tv":
            return flicktmdb().search_show(query=name, page=page, tags=tags, is_tv=True)
        elif show_type == "multi":
            return flicktmdb().search_general_show(query=name, page=page, tags=tags)
        if show_type == "anime":
            return flickanimelist().search_anime(query=name)
        return None

    @staticmethod
    def get_show_info_from_id(show_type, id):
        if show_type == "movie":
            return flicktmdb().get_show(tmdb_id=id, is_tv=False)
        elif show_type == "tv":
            return flicktmdb().get_show(tmdb_id=id, is_tv=True)
        elif show_type == "anime":
            return flickanimelist().get_anime(animelist_id=id)
        print("Only movie, tv, and anime show types are supported!")
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
