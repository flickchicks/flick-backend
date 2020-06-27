import datetime
import json
import os
import pprint as pp
import sys

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

import tmdbsimple as tmdb
from jikanpy import Jikan

from .models import Show
from .serializers import ShowSerializer
from tag.models import Tag

from django.db import IntegrityError


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
    def create_show_objects(show_info_lst):
        serializer_data = []
        for show_info in show_info_lst:
            if not show_info:
                continue
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
                show.save()
                if show_info.get("show_tags"):
                    for tag_name in show_info.get("show_tags"):
                        try:
                            show.tags.create(tag=tag_name)
                        except:
                            show.tags.add(Tag.objects.get(tag=tag_name))
                    show.save()
                serializer = ShowSerializer(show)
                serializer_data.append(serializer.data)
            except IntegrityError:
                show = Show.objects.get(
                    title=show_info.get("title"),
                    ext_api_id=show_info.get("ext_api_id"),
                    ext_api_source=show_info.get("ext_api_source"),
                )
                serializer = ShowSerializer(show)
                serializer_data.append(serializer.data)
            except Exception as e:
                print(e)
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
    def search_show_ids_by_name(show_type, name):
        """
        show_type can be 'movie', 'tv', or 'anime'
        """
        if show_type == "movie":
            api = TMDB_API()
            return api.search_movie_by_name(name)
        elif show_type == "tv":
            api = TMDB_API()
            return api.search_tv_by_name(name)
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


class TMDB_API:
    def get_movie_from_tmdb_info(self, info, credit):
        """
        get a flick movie object similar by parsing the
        information returned by movieDB
        """
        genres = info.get("genres")
        crew = credit.get("crew")
        cast = credit.get("cast")
        tags = [g.get("name") for g in genres] if genres else []
        cast_info = [p.get("name") for p in cast] if cast else []
        directors = []
        for c in crew:
            if c.get("job") == "Director":
                directors.append(c.get("name"))

        movie = {
            "show_id": info.get("id"),
            "title": info.get("original_title"),
            "poster_pic": settings.MOVIEDB_BASE_URL + info.get("poster_path"),
            "show_tags": tags,
            "is_tv": False,
            "date_released": info.get("release_date"),
            "duration": info.get("runtime"),
            "language": info.get("original_language"),
            "description": info.get("overview"),
            "directors": directors,
            "cast": cast_info,
        }

        return movie

    def get_tv_from_tmdb_info(self, info, credit):
        genres = info.get("genres")
        crew = credit.get("crew")
        cast = credit.get("cast")
        tags = [genre.get("name") for genre in genres] if genres else []
        cast_info = [p.get("name") for p in cast] if cast else []

        duration = info.get("episode_run_time")[0] if info.get("episode_run_time") else None
        producers = []
        for c in crew:
            if c.get("job") == "Producer":
                producers.append(c.get("name"))

        tv = {
            "show_id": info.get("id"),
            "title": info.get("original_name"),
            "poster_pic": settings.MOVIEDB_BASE_URL + info.get("poster_path"),
            "show_tags": tags,
            "is_tv": True,
            "date_released": info.get("first_air_date"),
            "duration": duration,
            "language": info.get("original_language"),
            "description": info.get("overview"),
            "status": info.get("status"),
            "directors": producers,
            "cast": cast_info,
        }

        return tv

    def get_show_ids_from_tmdb_search(self, search):
        """
        Given the most recent search, return the show ids.
        """
        return [movie_info["id"] for movie_info in search.results]

    def get_movie_info_from_id(self, id):
        try:
            movie = tmdb.Movies(id)
            return self.get_movie_from_tmdb_info(movie.info(), movie.credits())
        except Exception as e:
            print(e)
            return None

    def search_movie_by_name(self, name):
        """
        Search a movie by name, return a list of show ids.
        """
        search = tmdb.Search()
        search.movie(query=name)
        return self.get_show_ids_from_tmdb_search(search)

    def get_tv_info_from_id(self, id):
        try:
            tv = tmdb.TV(id)
            return self.get_tv_from_tmdb_info(tv.info(), tv.credits())
        except Exception as e:
            print(e)
            return None

    def get_movie_info_for_top_rated(self, info):
        credit = tmdb.Movies(info.get("id")).credits()
        return self.get_movie_from_tmdb_info(info, credit)

    def get_tv_info_for_top_rated(self, info):
        credit = tmdb.TV(info.get("id")).credits()
        return self.get_movie_from_tmdb_info(info, credit)

    def get_top_movie(self, page=1):
        """
        Get a list of top rated movie detailed info.
        """
        movie = tmdb.Movies()
        movie_info_lst = movie.top_rated(page=page).get("results")
        return [self.get_movie_from_top_rated(movie_info) for movie_info in movie_info_lst if movie_info]

    def get_top_tv(self, page=1):
        """
        Get a list of top rated TV detailed info.
        """
        tv = tmdb.TV()
        tv_info_lst = tv.top_rated(page=page).get("results")
        return [self.get_tv_info_from_top_rated(tv_info) for tv_info in tv_info_lst if tv_info]

    def search_tv_by_name(self, name):
        """
        Search a TV by name, return a list of ext_api_ids.
        """
        search = tmdb.Search()
        search.tv(query=name)
        return self.get_show_ids_from_tmdb_search(search)


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
        return [anime_info.get("mal_id") for anime_info in anime_info_lst]

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
