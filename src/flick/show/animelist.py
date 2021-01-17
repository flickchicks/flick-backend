from datetime import datetime

from mal import Anime
from mal import AnimeSearch


class flickanimelist:
    def get_anime(search, animelist_id):
        result = Anime(animelist_id)
        is_tv = True if result.type == "TV" else False
        duration = None
        print("result duration", result.duration)
        try:
            if is_tv:
                duration = result.duration.split(" min.")[0]
                print("duration", duration)
            else:
                date_split = result.duration.split(" hr. ")
                hrs = date_split[0]
                mins = date_split[1].split(" min.")[0]
                total_mins = int(hrs) * 60 + int(mins)
                duration = total_mins
        except Exception as e:
            print("Could not get duration for animelist:", e)
        directors = ", ".join(result.producers)
        try:
            first_date = result.aired.split(" to ")[0].split(" ")
            print("first_date", first_date)
            month = datetime.strptime(first_date[0], "%b").month
            print("month", month)
            if month < 10:
                # Jan is 01
                month = f"0{month}"
            day = first_date[1].split(",")[0]
            print("day", day)
            year = first_date[2]
            print("year", year)
            date_released = f"{year}-{month}-{day}"
            print("date_released", date_released)
        except Exception as e:
            print("Could not get first date", e)
            try:
                if result.premiered:
                    year = result.premiered.split(" ")[1]
                    date_released = year
            except:
                print("Could not get any dates for animelist api.")
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
            "premiered": result.premiered,
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
