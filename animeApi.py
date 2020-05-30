import json
import pprint as pp

from jikanpy import Jikan

jikan = Jikan()


class AnimeApi:
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


if __name__ == "__main__":
    db = AnimeApi()
    # test calls
    pp.pprint(db.search_animal_by_keyword("mushishi"))
