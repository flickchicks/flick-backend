from mal import AnimeSearch


class flickanimelist:
    def get_anime(search, animelist_id):
        pass

    def search_anime(self, query):
        results = AnimeSearch(query).results
        shows = []
        for result in results:
            show = {
                "title": result.title,
                "ext_api_id": result.mal_id,
                "ext_api_source": "animelist",
                "poster_pic": result.image_url,
                "is_tv": True if result.type == "TV" else False,
                "plot": result.synopsis,
                "episodes": result.episodes,
                "animelist_rating": result.score,
                "url": result.url,
                "language": "ja",
            }
            shows.append(show)
        return shows
