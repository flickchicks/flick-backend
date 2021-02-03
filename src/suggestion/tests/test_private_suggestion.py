import json

from api.tests import FlickTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show


class PrivateSuggestionTests(FlickTestCase):
    SUGGEST_URL = reverse("private-suggestion")
    SUGGESTIONS_URL = reverse("private-suggestion-list")
    ME_URL = reverse("me")

    def setUp(self):
        self.client = APIClient()
        self.show = self._create_show()
        self.user_token = self._create_user_and_login()
        self.friend1_token = self._create_user_and_login()
        self.friend2_token = self._create_user_and_login()
        self._create_friendship(user1=User.objects.get(id=1), user2=User.objects.get(id=2))
        self._create_friendship(user1=User.objects.get(id=1), user2=User.objects.get(id=3))

    def _create_show(self):
        show = Show()
        show.title = "title"
        show.ext_api_id = 1
        show.ext_api_source = "tmdb"
        show.poster_pic = "poster.pic"
        show.is_tv = True
        show.date_released = "4/1/20"
        show.status = "status"
        show.language = "en"
        show.duration = None
        show.plot = "juicy plot"
        show.seasons = 3
        show.directors = "alanna"
        show.cast = "alanna"
        show.save()
        return show

    def _suggest_show(self, token, suggest_data):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.post(self.SUGGEST_URL, suggest_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[-1]["show"]["id"], suggest_data.get("show_id"))
        self.assertEqual(data[-1]["message"], suggest_data.get("message"))

    def _check_suggestion(self, friend_token, suggest_data):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + friend_token)
        response = self.client.get(self.SUGGESTIONS_URL)
        data = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[-1]["show"]["id"], suggest_data.get("show_id"))
        self.assertEqual(data[-1]["message"], suggest_data.get("message"))

    def _check_me_has_num_notifs(self, friend_token, num_notifs):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + friend_token)
        response = self.client.get(self.ME_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("num_notifs"), num_notifs)

    def test_suggestions(self):
        suggest_data = {"users": [2, 3], "message": "Great film", "show_id": self.show.pk}
        self._suggest_show(self.user_token, suggest_data)
        self._check_suggestion(self.friend1_token, suggest_data)
        self._check_suggestion(self.friend2_token, suggest_data)
        self._check_me_has_num_notifs(self.friend1_token, 1)
        self._check_me_has_num_notifs(self.friend2_token, 1)

        # test suggestion already sent failure
        suggest_data = {"users": [2, 3], "message": "Great film", "show_id": self.show.pk}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.post(self.SUGGEST_URL, suggest_data, format="json")
        self.assertEqual(response.status_code, 404)
        error = json.loads(response.content)["error"]
        self.assertEqual(error, "Suggestion has already been sent!")
