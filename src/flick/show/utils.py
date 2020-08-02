import datetime
import pprint as pp

from django.conf import settings
from jikanpy import Jikan
from tag.models import Tag
import tmdbsimple as tmdb

from .models import Show
from .serializers import ShowSerializer


# create an instance of the Anime API
jikan = Jikan()

# set up the TMDB API access key from .env
tmdb.API_KEY = settings.TMDB_API_KEY

# Movie data format
"""
Movie object format
{
    ext_api_id:string
    title : string
    poster_pic : string
    show_tags: array
    is_tv: boolean
    date_released: string
    duration: integer
    language: string
    plot: string
}
"""


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
                serializer = ShowSerializer(show, context={"request": request})
                serializer_data.append(serializer.data)
            else:
                try:
                    show = Show()
                    show.title = show_info.get("title")
                    show.ext_api_id = show_info.get("ext_api_id")
                    show.ext_api_source = show_info.get("ext_api_source")
                    show.poster_pic = show_info.get("poster_pic")
                    show.is_tv = show_info.get("is_tv")
                    show.date_released = show_info.get("date_released")
                    show.status = show_info.get("status")
                    show.language = show_info.get("language")
                    show.duration = show_info.get("duration")
                    show.plot = show_info.get("plot")
                    show.seasons = show_info.get("seasons")
                    show.directors = show_info.get("directors")
                    show.cast = show_info.get("cast")
                    show.save()
                    if show_info.get("show_tags"):
                        for genre in show_info.get("show_tags"):
                            try:
                                show.tags.create(
                                    tag=genre.get("name"),
                                    ext_api_id=genre.get("id"),
                                    ext_api_source=show_info.get("ext_api_source"),
                                )
                            except:
                                show.tags.add(Tag.objects.get(tag=genre.get("name")))
                        show.save()
                    # elif show_info.get("ext_api_tags"):
                    #     for tag_id in show_info.get("ext_api_tags"):
                    #         tag = Tag.objects.filter(ext_api_id=tag_id, ext_api_source=show_info.get("ext_api_source"))
                    #         if tag:
                    #             show.tags.add(tag)
                    #         else:
                    #             print("oh no tag doesn't exist")
                    #             show.tags.create(
                    #                 tag=genre.get("name"),
                    #                 ext_api_id=genre.get("id"),
                    #                 ext_api_source=show_info.get("ext_api_source"),
                    #             )
                    # show.save()
                    serializer = ShowSerializer(show, context={"request": request})
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
    def search_show_ids_by_name(show_type, name, tags=[]):
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


class TMDB_API:
    def get_movie_from_tmdb_search(self, info):
        poster_path = info.get("poster_path")

        movie = {
            "ext_api_id": info.get("id"),
            "ext_api_source": "tmdb",
            "title": info.get("original_title"),
            "poster_pic": settings.TMDB_BASE_URL + poster_path if poster_path else None,
            "show_tags": info.get("genres"),
            "ext_api_tags": info.get("genre_ids"),
            "is_tv": False,
            "date_released": info.get("release_date"),
            "duration": datetime.timedelta(minutes=info.get("runtime", 0)),
            "language": info.get("original_language"),
            "plot": info.get("overview"),
            # "directors": directors,
            # "cast": cast_info,
        }
        return movie

    def get_movie_from_tmdb_info(self, info, credit):
        """
        get a flick movie object similar by parsing the
        information returned by movieDB
        """
        crew = credit.get("crew")
        cast = credit.get("cast")

        cast_info = [p.get("name") for p in cast] if cast else []
        directors = [c.get("name") for c in crew if c.get("job") == "Director"]

        directors = ", ".join(directors)
        cast_info = ", ".join(cast_info)

        poster_path = info.get("poster_path")

        movie = {
            "ext_api_id": info.get("id"),
            "ext_api_source": "tmdb",
            "title": info.get("original_title"),
            "poster_pic": settings.TMDB_BASE_URL + poster_path if poster_path else None,
            "show_tags": info.get("genres"),
            "ext_api_tags": info.get("genre_ids"),
            "is_tv": False,
            "date_released": info.get("release_date"),
            "duration": datetime.timedelta(minutes=info.get("runtime", 0)),
            "language": info.get("original_language"),
            "plot": info.get("overview"),
            "directors": directors,
            "cast": cast_info,
        }
        return movie

    def get_show_from_tmdb_info(self, info):
        poster_path = info.get("poster_path")

        show = {
            "ext_api_id": info.get("id"),
            "ext_api_source": "tmdb",
            "title": info.get("original_title"),
            "poster_pic": settings.TMDB_BASE_URL + poster_path if poster_path else None,
            "show_tags": info.get("genres"),
            "ext_api_tags": info.get("genre_ids"),
            "is_tv": False,
            "date_released": info.get("release_date"),
            "duration": datetime.timedelta(minutes=info.get("runtime", 0)),
            "language": info.get("original_language"),
            "plot": info.get("overview"),
            "seasons": info.get("number_of_seasons"),
        }
        return show

    def get_tv_from_tmdb_info(self, info, credit):
        # maybe need another separate json?? episodes/ last aired/ most recent episode etc
        crew = credit.get("crew")
        cast = credit.get("cast")

        duration = info.get("episode_run_time")[0] if info.get("episode_run_time") else 0

        cast_info = [p.get("name") for p in cast] if cast else []
        directors = [c.get("name") for c in crew if c.get("job") == "Producer"]

        directors = ", ".join(directors)
        cast_info = ", ".join(cast_info)

        poster_path = info.get("poster_path")

        tv = {
            "ext_api_id": info.get("id"),
            "ext_api_source": "tmdb",
            "title": info.get("original_name"),
            "poster_pic": settings.TMDB_BASE_URL + poster_path if poster_path else None,
            "show_tags": info.get("genres"),
            "ext_api_tags": info.get("genre_ids"),
            "is_tv": True,
            "date_released": info.get("first_air_date"),
            "duration": datetime.timedelta(minutes=duration),
            "language": info.get("original_language"),
            "plot": info.get("overview"),
            "status": info.get("status"),
            "seasons": info.get("number_of_seasons"),
            "directors": directors,
            "cast": cast_info,
        }
        return tv

    def discover_movies_by_genre(self, genre, page=1):
        discover = tmdb.Discover()
        movie_info_lst = discover.movie(page=page, with_genres=genre)
        return [
            self.get_movie_info_for_top_rated(movie_info) for movie_info in movie_info_lst.get("results") if movie_info
        ]

    def discover_tvs_by_genre(self, genre, page=1):
        discover = tmdb.Discover()
        tv_info_lst = discover.tv(page=page, with_genres=genre)
        return [self.get_tv_info_for_top_rated(tv_info) for tv_info in tv_info_lst.get("results") if tv_info]

    def get_show_ids_from_tmdb_search(self, search, tags):
        """
        Given the most recent search, return the show ids.
        """
        show_ids = []
        for show_info in search.results:
            if set(tags).issubset(set(show_info.get("genre_ids"))):
                show_ids.append(show_info.get("id"))
        return show_ids

    def get_shows_from_tmdb_search(self, search, tags):
        shows = []
        for show_info in search.results:
            if set(tags).issubset(set(show_info.get("genre_ids"))):
                shows.append(self.get_show_from_tmdb_info(show_info))
        return shows

    def get_movie_info_from_id(self, id):
        try:
            movie = tmdb.Movies(id)
            return self.get_movie_from_tmdb_info(movie.info(), movie.credits())
        except:
            return None

    def search_movie_by_name(self, name, tags):
        """
        Search a movie by name, return a list of show ids.
        """
        search = tmdb.Search()
        search.movie(query=name)
        # return self.get_show_ids_from_tmdb_search(search, tags)
        return self.get_shows_from_tmdb_search(search, tags)

    def get_tv_info_from_id(self, id):
        try:
            tv = tmdb.TV(id)
            return self.get_tv_from_tmdb_info(tv.info(), tv.credits())
        except:
            return None

    def get_movie_info_for_top_rated(self, info):
        credit = tmdb.Movies(info.get("id")).credits()
        return self.get_movie_from_tmdb_info(info, credit)

    def get_tv_info_for_top_rated(self, info):
        credit = tmdb.TV(info.get("id")).credits()
        return self.get_tv_from_tmdb_info(info, credit)

    def get_top_movie(self, page=1):
        """
        Get a list of top rated movie detailed info.
        """
        movie = tmdb.Movies()
        movie_info_lst = movie.top_rated(page=page).get("results")
        return [self.get_movie_info_for_top_rated(movie_info) for movie_info in movie_info_lst if movie_info]

    def get_top_tv(self, page=1):
        """
        Get a list of top rated TV detailed info.
        """
        tv = tmdb.TV()
        tv_info_lst = tv.top_rated(page=page).get("results")
        return [self.get_tv_info_for_top_rated(tv_info) for tv_info in tv_info_lst if tv_info]

    def search_tv_by_name(self, name, tags):
        """
        Search a TV by name, return a list of ext_api_ids.
        """
        search = tmdb.Search()
        search.tv(query=name)
        # return []
        # return self.get_show_ids_from_tmdb_search(search, tags)
        return self.get_shows_from_tmdb_search(search, tags)


class AnimeList_API:
    """
    Anime Object
    {
        ext_api_id:string
        title : string
        poster_pic : string
        is_tv: boolean
        date_released: string
        status: string
        plot: string
        duration: string
    }
    """

    def get_anime_from_animelist_info(self, info):
        """
        Filter information from the API, returns an Anime Object.
        """
        duration = datetime.timedelta(minutes=info.get("duration")) if info.get("duration") else None
        anime = {
            "ext_api_id": info.get("mal_id"),
            "ext_api_source": "animelist",
            "title": info.get("title"),
            "poster_pic": info.get("image_url"),
            "is_tv": True,  # assuming
            "date_released": info.get("start_date"),
            "plot": info.get("synopsis"),
            "status": info.get("status"),
            "duration": duration,
        }
        return anime

    def get_anime_info_from_id(self, id):
        """
        Search anime by the mal_id from animelist API, returns an Anime Object.
        """
        try:
            anime_info = jikan.anime(id)
            return self.get_anime_from_animelist_info(anime_info)
        except:
            return None

    def search_anime_by_name(self, name):
        """
        Search anime by the mal_id from animelist API, returns a list of anime ids.
        """
        anime_info_lst = jikan.search("anime", name, page=1).get("results")
        return [self.get_anime_from_animelist_info(anime) for anime in anime_info_lst]
        # return [anime_info.get("mal_id") for anime_info in anime_info_lst]

    def search_anime_by_year(self, year, season):
        """
        Search anime by year and season from anime API, returns a list of anime ids.
        """
        anime_info_lst = jikan.season(year=year, season=season).get("anime")
        return [anime_info.get("mal_id") for anime_info in anime_info_lst]

    def get_top_anime(self):
        """
        Get top anime from animelist API, returns a list of anime ids.
        """
        anime_info_lst = jikan.top(type="anime").get("top")
        return [self.get_anime_from_animelist_info(anime_info) for anime_info in anime_info_lst if anime_info]
