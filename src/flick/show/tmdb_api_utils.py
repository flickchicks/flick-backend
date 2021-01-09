import datetime
import json

from django.conf import settings
import requests
import tmdbsimple as tmdb

# set up the TMDB API access key from .env
tmdb.API_KEY = settings.TMDB_API_KEY


class TMDB_API:
    def get_providers_from_movie_id(self, movie_id):
        url = f"{settings.TMDB_BASE_URL}/movie/{movie_id}/watch/providers?api_key={tmdb.API_KEY}"
        r = requests.get(url)
        if r.status_code != 200:
            return []
        try:
            d = json.loads(r.content)
            results = d.get("results")
            us = results.get("US")
            rent = us.get("rent") or []
            buy = us.get("buy") or []
            flatrate = us.get("flatrate") or []
            data = rent + buy + flatrate
            providers = []
            for p in data:
                provider_name = p.get("provider_name")
                provider_image = settings.TMDB_BASE_IMAGE_URL + p.get("logo_path")
                providers.append({"name": provider_name, "image": provider_image})
        except:
            return []
        return providers

    def get_providers_from_tv_id(self, tv_id):
        url = f"{settings.TMDB_BASE_URL}/tv/{tv_id}/watch/providers?api_key={tmdb.API_KEY}"
        r = requests.get(url)
        if r.status_code != 200:
            return []
        try:
            d = json.loads(r.content)
            results = d.get("results")
            us = results.get("US")
            buy = us.get("buy") or []
            flatrate = us.get("flatrate") or []
            data = buy + flatrate
            providers = []
            for p in data:
                provider_name = p.get("provider_name")
                provider_image = settings.TMDB_BASE_IMAGE_URL + p.get("logo_path")
                providers.append({"name": provider_name, "image": provider_image})
        except:
            return []
        return providers

    def get_show_from_tmdb_info(self, info, is_tv):
        poster_path = info.get("poster_path")
        if is_tv:
            duration = info.get("episode_run_time")[0] if info.get("episode_run_time") else 0
        else:
            duration = info.get("runtime", 0)

        show = {
            "ext_api_id": info.get("id"),
            "ext_api_source": "tmdb",
            "title": info.get("original_name" if is_tv else "original_title"),
            "poster_pic": settings.TMDB_BASE_IMAGE_URL + poster_path if poster_path else None,
            "ext_api_genres": info.get("genres"),
            "is_tv": is_tv,
            "date_released": info.get("first_air_date" if is_tv else "release_date"),
            "duration": datetime.timedelta(minutes=duration),
            "language": info.get("original_language"),
            "plot": info.get("overview"),
            "seasons": info.get("number_of_seasons"),
        }
        return show

    def get_detailed_movie_from_tmdb_info(self, info, credits):
        """
        get a flick movie object similar by parsing the
        information returned by movieDB
        """
        crew = credits.get("crew")
        directors = [c.get("name") for c in crew if c.get("job") == "Director"]
        directors = ", ".join(directors)

        cast = credits.get("cast")
        cast_info = [p.get("name") for p in cast] if cast else []
        cast_info = ", ".join(cast_info)

        poster_path = info.get("poster_path")
        providers = self.get_providers_from_movie_id(info.get("id"))

        movie = {
            "ext_api_id": info.get("id"),
            "ext_api_source": "tmdb",
            "title": info.get("original_title"),
            "poster_pic": settings.TMDB_BASE_IMAGE_URL + poster_path if poster_path else None,
            "ext_api_genres": info.get("genres"),
            "is_tv": False,
            "date_released": info.get("release_date"),
            "duration": datetime.timedelta(minutes=info.get("runtime", 0)),
            "language": info.get("original_language"),
            "plot": info.get("overview"),
            "directors": directors,
            "cast": cast_info,
            "imdb_id": info.get("imdb_id"),
            "providers": providers,
        }
        return movie

    def get_detailed_tv_from_tmdb_info(self, info, credits):
        # maybe need another separate json?? episodes/ last aired/ most recent episode etc
        crew = credits.get("crew")
        directors = [c.get("name") for c in crew if c.get("job") == "Producer"]
        directors = ", ".join(directors)

        cast = credits.get("cast")
        cast_info = [p.get("name") for p in cast] if cast else []
        cast_info = ", ".join(cast_info)

        duration = info.get("episode_run_time")[0] if info.get("episode_run_time") else 0
        poster_path = info.get("poster_path")
        providers = self.get_providers_from_tv_id(info.get("id"))

        tv = {
            "ext_api_id": info.get("id"),
            "ext_api_source": "tmdb",
            "title": info.get("original_name"),
            "poster_pic": settings.TMDB_BASE_IMAGE_URL + poster_path if poster_path else None,
            "ext_api_genres": info.get("genres"),
            "is_tv": True,
            "date_released": info.get("first_air_date"),
            "duration": datetime.timedelta(minutes=duration),
            "language": info.get("original_language"),
            "plot": info.get("overview"),
            "status": info.get("status"),
            "seasons": info.get("number_of_seasons"),
            "directors": directors,
            "cast": cast_info,
            "providers": providers,
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

    def get_movie_info_from_id(self, id):
        try:
            movie = tmdb.Movies(id)
            return self.get_detailed_movie_from_tmdb_info(movie.info(), movie.credits())
        except:
            return None

    def get_tv_info_from_id(self, id):
        try:
            tv = tmdb.TV(id)
            return self.get_detailed_tv_from_tmdb_info(tv.info(), tv.credits())
        except:
            return None

    def get_movie_info_for_top_rated(self, info):
        credits = tmdb.Movies(info.get("id")).credits()
        return self.get_detailed_movie_from_tmdb_info(info, credits)

    def get_tv_info_for_top_rated(self, info):
        credits = tmdb.TV(info.get("id")).credits()
        return self.get_detailed_tv_from_tmdb_info(info, credits)

    def get_top_movie(self, page=1):
        """
        Get a list of top rated movie detailed info.
        """
        movie = tmdb.Movies()
        movie_info_lst = movie.top_rated(page=page).get("results")
        return [self.get_movie_info_for_top_rated(movie_info) for movie_info in movie_info_lst if movie_info]

    def get_popular_movie(self, page=1):
        """
        Get a list of top rated movie detailed info.
        """
        movie = tmdb.Movies()
        movie_info_lst = movie.popular(page=page).get("results")
        return [self.get_movie_info_for_top_rated(movie_info) for movie_info in movie_info_lst if movie_info]

    def get_now_playing_movie(self, page=1):
        """
        Get a list of top rated movie detailed info.
        """
        movie = tmdb.Movies()
        movie_info_lst = movie.now_playing(page=page).get("results")
        return [self.get_movie_info_for_top_rated(movie_info) for movie_info in movie_info_lst if movie_info]

    def get_top_tv(self, page=1):
        """
        Get a list of top rated TV detailed info.
        """
        tv = tmdb.TV()
        tv_info_lst = tv.top_rated(page=page).get("results")
        return [self.get_tv_info_for_top_rated(tv_info) for tv_info in tv_info_lst if tv_info]

    def get_popular_tv(self, page=1):
        """
        Get a list of top rated TV detailed info.
        """
        tv = tmdb.TV()
        tv_info_lst = tv.popular(page=page).get("results")
        return [self.get_tv_info_for_top_rated(tv_info) for tv_info in tv_info_lst if tv_info]

    def get_now_playing_tv(self, page=1):
        """
        Get a list of top rated TV detailed info.
        """
        tv = tmdb.TV()
        tv_info_lst = tv.airing_today(page=page).get("results")
        return [self.get_tv_info_for_top_rated(tv_info) for tv_info in tv_info_lst if tv_info]
