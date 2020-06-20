import json
import os
import pprint as pp
import sys

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

import tmdbsimple as tmdb
from jikanpy import Jikan

# create an instance of the Anime API
jikan = Jikan()

# set up the TMDB API access key from .env
tmdb.API_KEY = settings.TMDB_API_KEY

# base URL for posters
BASE_MOVIE_URL = "http://image.tmdb.org/t/p/w185"

# Movie data format
"""
Movie object format
{
    show_id:string
    title : string
    poster_pic : string
    show_tags: array
    is_tv: boolean
    date_released: string
    duration: integer
    language: string
    description: string
}
"""


def get_movie_from_DBinfo(info, credit):
    """
    get a flick movie object similar by parsing the
    information returned by movieDB
    """
    genres = info.get("genres")
    crew = credit.get("crew")
    cast = credit.get("cast")
    tags = [g.get("name") for g in genres] if genres else []
    castInfo = [p.get("name") for p in cast] if cast else []
    directors = []
    for c in crew:
        if c.get("job") == "Director":
            directors.append(c.get("name"))

    movie = {
        "show_id": info.get("id"),
        "title": info.get("original_title"),
        "poster_pic": BASE_MOVIE_URL + info.get("poster_path"),
        "show_tags": tags,
        "is_tv": False,
        "date_released": info.get("release_date"),
        "duration": info.get("runtime"),
        "language": info.get("original_language"),
        "description": info.get("overview"),
        "director(s)": directors,
        "cast": castInfo,
    }

    return movie


def get_tv_from_DBinfo(info, credit):
    # maybe need another separate json?? episodes/ last aired/ most recent episode etc
    genres = info.get("genres")
    crew = credit.get("crew")
    cast = credit.get("cast")
    tags = [genre.get("name") for genre in genres] if genres else []
    castInfo = [p.get("name") for p in cast] if cast else []

    duration = info.get("episode_run_time")[0] if info.get("episode_run_time") else None
    producers = []
    for c in crew:
        if c.get("job") == "Producer":
            producers.append(c.get("name"))

    tv = {
        "show_id": info.get("id"),
        "title": info.get("original_name"),
        "poster_pic": BASE_MOVIE_URL + info.get("poster_path"),
        "show_tags": tags,
        "is_tv": True,
        "date_released": info.get("first_air_date"),
        "duration": duration,
        "language": info.get("original_language"),
        "description": info.get("overview"),
        "status": info.get("status"),
        "director(s)": producers,
        "cast": castInfo,
    }

    return tv


def get_movie_info(id):
    """
        Get movie info by id
    """
    movie = tmdb.Movies(id)
    try:
        return get_movie_from_DBinfo(movie.info(), movie.credits())
    except Exception as e:
        print(e)
        return None


def search_result(search):
    """
        given the most recent search,
        return the media ids
    """
    movie_ids = [movie_info["id"] for movie_info in search.results]
    return movie_ids


def get_tv_info(id):
    """
        Get tv info by id
    """
    tv = tmdb.TV(id)
    try:
        return get_tv_from_DBinfo(tv.info(), tv.credits())
    except Exception as e:
        print(e)
        return None


def get_anime_from_DBinfo(info):
    """
    filter information from the API
    returns a Anime Json object
    """
    anime = {
        "show_id": info.get(["mal_id"]),
        "title": info["title"],
        "poster_pic": info["image_url"],
        "is_tv": True,  # assuming
        "date_released": info["aired"]["from"],
        "description": info["synopsis"],
        "status": info["status"],
        "duration": info["duration"],
    }
    return anime


def search_anime(id):
    try:
        search_result = jikan.anime(id)
        return get_anime_from_DBinfo(search_result)
    except:
        return None


class TMDB_API:
    # Movie helpers

    @staticmethod
    def get_movie_info_from_id(id):
        """
            Get movie detailed info by id
        """
        info = get_movie_info(id)
        if info is not None:
            return info
        return f"The movie ID {id} does not exist."

    @staticmethod
    def search_movie_by_name(name):
        """
            search a movie by name:
            return a list of media ids
        """
        search = tmdb.Search()
        search.movie(query=name)
        show_ids = search_result(search)
        return show_ids

    @staticmethod
    def get_tv_info_from_id(id):
        """
            Get TV detailed info by id
        """
        info = get_tv_info(id)
        try:
            return info
        except:
            return f"The TV ID {id} does not exist."

    @staticmethod
    def get_top_movie(page=1):
        """
            Get a list of top rated movie detailed info
        """
        movie = tmdb.Movies()
        lst = movie.top_rated(page=page).get("results")
        movies = []
        for movie_info in lst:
            info = get_movie_from_DBinfo(movie_info)
            if info is not None:
                movies.append(info)
        movies

    @staticmethod
    def get_top_tv(page=1):
        """
            Get a list of top rated TV detailed info
        """
        tv = tmdb.TV()
        lst = tv.top_rated(page=page).get("results")
        tvs = []
        for tv_info in lst:
            info = get_tv_from_DBinfo(tv_info)
            if info is not None:
                tvs.append(info)
        return tvs

    @staticmethod
    def search_tv_by_name(name):
        """
            search a TV by name:
            return a list of media ids
        """
        search = tmdb.Search()
        search.tv(query=name)
        show_ids = search_result(search)
        return show_ids

    @staticmethod
    # testing function for all info from search
    def info_from_search(search_lst, is_tv):
        """
            given a list of media IDs from search and the boolean is_tv,
            give back a list of detailed info
        """
        movies = []
        for movie_id in search_lst:
            info = get_tv_info(movie_id) if is_tv else get_movie_info(movie_id)
            if info is not None:
                movies.append(info)
        return movies


# Anime Data format

"""
Anime json object
{
    show_id:string
    title : string
    poster_pic : string
    is_tv: boolean
    date_released: string
    status: string
    description: string
    duration: string
}
"""


class AnimeList_API:
    # Anime helpers

    @staticmethod
    def search_anime_by_id(id):
        """
        search anime by the mal_id from anime API
        returns a Animal object
        """
        info = search_anime(id)
        if info is not None:
            return info
        else:
            return f"The anime ID {id} does not exist."

    @staticmethod
    def search_anime_by_keyword(keyword):
        """
        search anime by the mal_id from anime API
        returns a list of Anime id
        """
        result = []
        search_result = jikan.search("anime", keyword, page=1).get("results")
        for anime_info in search_result:
            result.append({"id": anime_info.get("mal_id")})
        return result

    @staticmethod
    def search_anime_by_year(year, season):
        """
        search anime by year and season from anime API
        returns a list of Anime id
        """
        result = []
        search_result = jikan.season(year=year, season=season).get("anime")
        for anime_info in search_result:
            result.append({"id": anime_info.get("mal_id")})
        return result

    @staticmethod
    def get_top_anime():
        """
        get Top animes from anime API
        returns a list of Animal id
        """
        result = []
        search_result = jikan.top(type="anime").get("top")
        for anime_info in search_result:
            result.append({"id": anime_info.get("mal_id")})
        return result

    @staticmethod
    def anime_info_from_search(search_lst):
        animes = []
        for anime in search_lst:
            info = search_anime(anime.get("id"))
            if info is not None:
                animes.append(info)
        return animes
