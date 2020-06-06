from rest_framework import status
from rest_framework.response import Response
import tmdbsimple as tmdb
from jikanpy import Jikan
import os
import sys
import json
import pprint as pp


# create an instance of the Anime API
jikan = Jikan()

# set up the TMDB API access key from .env
tmdb.API_KEY = os.getenv("TMDB_API_KEY")

# Movie data format
"""
Movie object format
{
media_id:string
title : string
poster_pic : string
director : string
media_tags: array #for now we use genre ids
is_tv: boolean
date_released: string
duration: string
language: string
description: string
}
"""


def success_response(data, status=status.HTTP_200_OK):
    return Response(json.dumps({"success": True, "data": data}), status=status)


def failure_response(message, status=status.HTTP_404_NOT_FOUND):
    return Response(json.dumps({"success": False, "error": message}), status=status)


def get_movie_from_DBinfo(info):
    """
    get a flick movie object similar by parsing the
    information returned by movieDB
    """
    tags = []
    for genre in info["genres"]:
        tags.append(genre["name"])

    movie = json.dumps(
        {
            "media_id": info["id"],
            "title": info["original_title"],
            "poster_pic": info["poster_path"],
            "media_tags": tags,
            "is_tv": False,
            "date_released": info["release_date"],
            "duration": info["runtime"],
            "language": info["original_language"],
            "description": info["overview"],
        }
    )
    return movie


def get_tv_from_DBinfo(info):
    # maybe need another separate json?? episodes/ last aired/ most recent episode etc
    tags = []
    for genre in info["genres"]:
        tags.append(genre["name"])

    tv = json.dumps(
        {
            "media_id": info["id"],
            "title": info["original_name"],
            "poster_pic": info["poster_path"],
            "media_tags": tags,
            "is_tv": True,
            "date_released": info["first_air_date"],
            #  'duration': info['runtime'],
            "language": info["original_language"],
            "description": info["overview"],
            "status": info["status"],
        }
    )
    return tv


def get_movie_info(id):
    """
        Get movie info by id
    """
    movie = tmdb.Movies(id)
    try:
        return TMDB_API.get_movie_from_DBinfo(movie.info())
    except:
        return None


def search_result(search):
    """
        given the most recent search,
        return the media ids
    """
    result = []
    for movie_info in search.results:
        movie_id = movie_info["id"]
        result.append(movie_id)
    return result


def get_tv_info(id):
    """
        Get tv info by id
    """
    tv = tmdb.TV(id)
    try:
        return get_tv_from_DBinfo(tv.info())
    except:
        return None


def get_anime_from_DBinfo(info):
    """
    filter information from the API
    returns a Anime Json object
    """
    return json.dumps(
        {
            "media_id": info["mal_id"],
            "title": info["title"],
            "poster_pic": info["image_url"],
            "is_tv": True,  # assuming
            "date_released": info["aired"]["from"],
            "description": info["synopsis"],
            "status": info["status"],
            "duration": info["duration"],
        }
    )


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
        info = get_movie_info(id)
        if info is not None:
            return success_response(info)
        else:
            return failure_response("The movie ID {} does not exist.".format(id))

    @staticmethod
    def search_movie_by_name(name):
        """
            search a movie by name:
            return a list of media ids
        """
        search = tmdb.Search()
        search.movie(query=name)
        return success_response(search_result(search))

    @staticmethod
    def get_tv_info_from_id(id):
        """
            Get movie info by id
        """
        info = get_tv_info(id)
        try:
            return success_response(info)
        except:
            return failure_response("The TV ID {} does not exist.".format(id))

    @staticmethod
    def get_top_movie(page=1):
        movie = tmdb.Movies()
        lst = movie.top_rated(page)["results"]
        movies = []
        for movie_info in lst:
            info = get_movie_from_DBinfo(movie_info)
            if info is not None:
                movies.append(info)
        return success_response(movies)

    @staticmethod
    def get_top_tv(page=1):
        tv = tmdb.TV()
        lst = tv.top_rated(page)["results"]
        tvs = []
        for tv_info in lst:
            info = get_tv_from_DBinfo(tv_info)
            if info is not None:
                tvs.append(info)
        return success_response(tvs)

    @staticmethod
    def search_tv_by_name(name):
        """
            search a movie by name:
            return a list of media ids
        """
        search = tmdb.Search()
        search.tv(query=name)
        return success_response(search_result(search))

    @staticmethod
    # testing function for all info from search
    def infos_from_search(search_lst, is_tv):
        """
            given a list of media IDs from search and the boolean is_tv,
            give back a list of movie infos
        """
        movies = []
        for movie_id in search_lst:
            info = get_tv_info(movie_id) if is_tv else get_movie_info(movie_id)
            if info is not None:
                movies.append(info)
        return success_response(movies)


# Anime Data format

"""
Anime json object
{
    media_id:string
    title : string
    poster_pic : string
    is_tv: boolean
    date_released: string
    status: string
    description: string
    duration: string
}
"""


class Anim_API:
    # Anime helpers

    @staticmethod
    def search_anime_by_id(id):
        """
        search anime by the mal_id from anime API
        returns a Animal object
        """
        info = search_anime(id)
        if info is not None:
            return success_response(info)
        else:
            return failure_response("The anime ID {} does not exist.".format(id))

    @staticmethod
    def search_anime_by_keyword(keyword):
        """
        search anime by the mal_id from anime API
        returns a list of Anime id
        """
        result = []
        search_result = jikan.search("anime", keyword, page=1)["results"]
        for anime_info in search_result:
            result.append({"id": anime_info["mal_id"]})
        return success_response(result)

    @staticmethod
    def search_anime_by_year(year, season):
        """
        search anime by year and season from anime API
        returns a list of Anime id
        """
        result = []
        search_result = jikan.season(year=year, season=season)["anime"]
        for anime_info in search_result:
            result.append({"id": anime_info["mal_id"]})
        return success_response(result)

    @staticmethod
    def get_top_anime():
        """
        get Top animes from anime API
        returns a list of Animal id
        """
        result = []
        search_result = jikan.top(type="anime")["top"]
        for anime_info in search_result:
            result.append({"id": anime_info["mal_id"]})
        return success_response(result)

    @staticmethod
    def anime_infos_from_search(search_lst):
        animes = []
        for anime in search_lst:
            info = search_anime(anime["id"])
            if info is not None:
                animes.append(info)
        return success_response(animes)
