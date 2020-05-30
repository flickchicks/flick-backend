import json
import os
import pprint as pp

import tmdbsimple as tmdb
from settings import TMDB_API_KEY


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


class MovieDBAPI:
    def __init__(self):
        tmdb.API_KEY = TMDB_API_KEY

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
            info = (
                self.get_tv_info(movie_id) if is_tv else self.get_movie_info(movie_id)
            )
            movies.append(info)
        return movies


if __name__ == "__main__":
    db = MovieDBAPI()
    # get movie by ID
    pp.pprint(db.get_movie_info(466282))
    # get movie by name search
    movie_search = db.search_movie_by_name("Avengers")
    pp.pprint(db.infos_from_search(movie_search, False))
    # get tv by name search
    tv_search = db.search_tv_by_name("gone")
    pp.pprint(db.infos_from_search(tv_search, True))
