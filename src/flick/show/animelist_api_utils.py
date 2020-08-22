import datetime

from jikanpy import Jikan
import tmdbsimple as tmdb

# create an instance of the Anime API
jikan = Jikan()


class AnimeList_API:
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
