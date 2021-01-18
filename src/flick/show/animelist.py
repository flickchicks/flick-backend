from datetime import datetime
from datetime import timedelta

from jikanpy import Jikan
from mal import Anime
from mal import AnimeSearch

jikan = Jikan()


class flickanimelist:
    def get_anime_helper(self, animelist_id):
        info = jikan.anime(animelist_id)
        try:
            duration = timedelta(minutes=int(info.get("duration"))) if info.get("duration") else None
        except:
            try:
                duration = int(info.get("duration").split(" min")[0])
            except:
                duration = None
        start_date = info.get("start_date")
        if start_date:
            start_date = start_date.split("T")[0]
        return {
            "date_released": start_date,
            "duration": duration,
        }

    def get_anime(self, animelist_id):
        result = Anime(animelist_id)
        is_tv = True if result.type == "TV" else False
        duration = None
        date_released = None
        try:
            if is_tv:
                duration = result.duration.split(" min.")[0]
            else:
                date_split = result.duration.split(" hr. ")
                hrs = date_split[0]
                if len(date_split) == 1:
                    mins = hrs.split(" min.")[0]
                else:
                    mins = date_split[1].split(" min.")[0]
                total_mins = int(hrs) * 60 + int(mins)
                duration = total_mins
        except:
            try:
                helper = self.get_anime_helper(animelist_id)
                duration = helper.get("duration")
            except:
                pass
        directors = ", ".join(result.producers)
        try:
            first_date = result.aired.split(" to ")[0].split(" ")
            month = datetime.strptime(first_date[0], "%b").month
            if month < 10:
                # Jan is 01
                month = f"0{month}"
            day = first_date[1].split(",")[0]
            if day < 10:
                day = f"0{day}"
            year = first_date[2]
            date_released = f"{year}-{month}-{day}"
        except:
            try:
                if result.premiered:
                    year = result.premiered.split(" ")[1]
                    date_released = year
            except:
                try:
                    helper = self.get_anime_helper(animelist_id)
                    date_released = helper.get("date_released")
                except:
                    pass
        return {
            "title": result.title_english,
            "ext_api_id": result.mal_id,
            "ext_api_source": "animelist",
            "ext_api_genres": result.genres,
            "poster_pic": result.image_url,
            "episodes": result.episodes,
            "date_released": date_released,
            "status": result.status,
            "language": "ja",
            "directors": directors,
            "is_tv": is_tv,
            "duration": duration,
            "plot": result.synopsis,
            "animelist_rating": result.score,
            "animelist_rank": result.rank,
            # "rating": result.rating,
        }

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
                "language": "ja",
            }
            shows.append(show)
        return shows
