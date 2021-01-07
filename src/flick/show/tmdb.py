import json

from django.conf import settings
import requests


class flicktmdb:
    def get_show(self, tmdb_id, is_tv=False):
        show_type = "tv" if is_tv else "movie"
        url = f"{settings.TMDB_BASE_URL}/{show_type}/{tmdb_id}?api_key={settings.TMDB_API_KEY}"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        result = json.loads(r.content)
        if is_tv:
            duration = result.get("episode_run_time")[0] if result.get("episode_run_time") else 0
        else:
            duration = result.get("runtime", 0)
        backdrop_path = result.get("backdrop_path")
        poster_path = result.get("poster_path")
        credits = self.get_credits(tmdb_id, is_tv)
        providers = self.get_providers(tmdb_id, is_tv)

        return {
            "backdrop_pic": settings.TMDB_BASE_IMAGE_URL + backdrop_path if backdrop_path else None,
            "cast": credits.get("cast"),
            "date_released": result.get("first_air_date" if is_tv else "release_date"),
            "directors": credits.get("directors"),
            "duration": duration,
            "ext_api_id": result.get("id"),
            "ext_api_source": "tmdb",
            "ext_api_genres": result.get("genres"),
            "homepage": result.get("homepage"),
            "is_adult": result.get("adult"),
            "is_tv": is_tv,
            "language": result.get("original_language"),
            "plot": result.get("overview"),
            "poster_pic": settings.TMDB_BASE_IMAGE_URL + poster_path if poster_path else None,
            "providers": providers,
            "seasons": result.get("number_of_seasons"),
            "status": result.get("status"),
            "tagline": result.get("tagline"),
            "title": result.get("original_name" if is_tv else "original_title"),
        }

    def get_credits(self, tmdb_id, is_tv=False):
        show_type = "tv" if is_tv else "movie"
        url = f"{settings.TMDB_BASE_URL}/{show_type}/{tmdb_id}/credits?api_key={settings.TMDB_API_KEY}"
        r = requests.get(url)
        if r.status_code != 200:
            return {
                "cast": [],
                "directors": [],
            }
        credits = json.loads(r.content)
        crew = credits.get("crew")
        directors = [c.get("name") for c in crew if c.get("job") == "Director"]
        directors = ", ".join(directors)

        cast = credits.get("cast")
        cast = [p.get("name") for p in cast] if cast else []
        cast = ", ".join(cast)

        return {
            "cast": cast,
            "directors": directors,
        }

    def get_providers(self, tmdb_id, is_tv=False):
        show_type = "tv" if is_tv else "movie"
        url = f"{settings.TMDB_BASE_URL}/{show_type}/{tmdb_id}/watch/providers?api_key={settings.TMDB_API_KEY}"
        r = requests.get(url)
        if r.status_code != 200:
            return []
        try:
            results = json.loads(r.content).get("results")
            us = results.get("US")
            rent = us.get("rent", [])
            buy = us.get("buy", [])
            flatrate = us.get("flatrate", [])
            data = rent + buy + flatrate
            providers = []
            for p in data:
                provider_name = p.get("provider_name")
                provider_image = settings.TMDB_BASE_IMAGE_URL + p.get("logo_path")
                providers.append({"name": provider_name, "image": provider_image})
        except Exception as e:
            print(f"Could not get providers from {tmdb_id}", e)
            return []
        return providers

    def search_show(self, query, page=1, tags=[], language="en-US", year=None, include_adult=False, is_tv=False):
        print("search show", page)
        show_type = "tv" if is_tv else "movie"
        url = f"{settings.TMDB_BASE_URL}/search/{show_type}?query={query}&language={language}&page={page}&api_key={settings.TMDB_API_KEY}"
        if year and is_tv:
            url += f"&first_air_date_year={year}"
        elif year and not is_tv:
            url += f"&year={year}"
        r = requests.get(url)
        if r.status_code != 200:
            return []
        results = json.loads(r.content).get("results")
        shows = []
        for result in results:
            if not set(tags).issubset(set(result.get("genre_ids"))):
                continue
            backdrop_path = result.get("backdrop_path")
            poster_path = result.get("poster_path")
            show = {
                "backdrop_pic": settings.TMDB_BASE_IMAGE_URL + backdrop_path if backdrop_path else None,
                "date_released": result.get("first_air_date" if is_tv else "release_date"),
                "ext_api_id": result.get("id"),
                "ext_api_source": "tmdb",
                "is_adult": result.get("adult"),
                "is_tv": is_tv,
                "language": result.get("original_language"),
                "plot": result.get("overview"),
                "poster_pic": settings.TMDB_BASE_IMAGE_URL + poster_path if poster_path else None,
                "title": result.get("original_name" if is_tv else "original_title"),
            }
            shows.append(show)
        return shows
