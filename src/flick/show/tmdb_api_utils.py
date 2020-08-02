import datetime
import pprint as pp

from django.conf import settings
import tmdbsimple as tmdb

# set up the TMDB API access key from .env
tmdb.API_KEY = settings.TMDB_API_KEY


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
        # print("genres", info.get("genres"))
        # print("genre_ids", info.get("genre_ids"))

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
        return self.get_shows_from_tmdb_search(search, tags)
