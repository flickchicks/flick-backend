import json
import os
import pprint as pp
import tmdbsimple as tmdb
from jikanpy import Jikan
from settings import TMDB_API_KEY


# create an instance of the Anime API
jikan = Jikan()

# set up the TMDB API access key from .env
tmdb.API_KEY = TMDB_API_KEY

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


# Movie helpers
def get_movie_from_DBinfo(self, info):
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


def get_tv_from_DBinfo(self, info):
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


def get_movie_info(self, id):
    """
        Get movie info by id
    """
    movie = tmdb.Movies(id)
    try:
        return self.get_movie_from_DBinfo(movie.info())
    except Exception as e:
        print(e)
        return None


def search_movie_by_name(self, name):
    """
        search a movie by name:
        return a list of media ids and tiles
    """
    search = tmdb.Search()
    search.movie(query=name)
    return self.search_result(search)


def get_tv_info(self, id):
    """
        Get movie info by id
    """
    tv = tmdb.TV(id)
    try:
        return self.get_tv_from_DBinfo(tv.info())
    except Exception as e:
        print(e)
        return None


def search_tv_by_name(self, name):
    """
        search a movie by name:
        return a list of media ids and tiles
    """
    search = tmdb.Search()
    search.tv(query=name)
    return self.search_result(search)


def search_result(self, search):
    """
        given the most recent search,
        return the movie_ids
    """
    result = []
    for movie_info in search.results:
        movie_id = movie_info["id"]
        result.append(movie_id)
    return result


def infos_from_search(self, search_lst, is_tv):
    movies = []
    for movie_id in search_lst:
        info = self.get_tv_info(movie_id) if is_tv else self.get_movie_info(movie_id)
        movies.append(info)
    return movies

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


# Anime helpers
def get_anime_from_DBinfo(self, info):
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


def search_anime_by_id(self, id):
    """
    search anime by the mal_id from anime API
    returns a Animal object
    """
    search_result = jikan.anime(id)
    return self.get_anime_from_DBinfo(search_result)


def search_animal_by_keyword(self, keyword):
    """
    search anime by the mal_id from anime API
    returns a list of Animal title and id
    """
    result = []
    search_result = jikan.search("anime", keyword, page=1)["results"]
    for anime_info in search_result:
        result.append({"title": anime_info["title"], "id": anime_info["mal_id"]})
    return result


def search_animal_by_year(self, year, season):
    """
    search anime by year and season from anime API
    returns a list of Animal title and id
    """
    result = []
    search_result = jikan.season(year=year, season=season)["anime"]
    for anime_info in search_result:
        result.append({"title": anime_info["title"], "id": anime_info["mal_id"]})
    return result


def get_top_anime(self):
    """
    get Top animes from anime API
    returns a list of Animal title and id
    """
    results = []
    search_result = jikan.top(type="anime")["top"]
    for anime_info in search_result:
        results.append({"title": anime_info["title"], "id": anime_info["mal_id"]})
    return results
