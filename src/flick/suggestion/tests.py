import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show


class PrivateSuggestionTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")

    def setUp(self):
        self.client = APIClient()
        self.show = self._create_show()
        self.user_token = self._create_user_and_login()
        self.friend1_token = self._create_user_and_login()
        self.friend2_token = self._create_user_and_login()
        self.SUGGESTION_URL = reverse("private-suggestion")

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

    def _create_user_and_login(self):
        """Returns the auth token."""
        letters = string.digits
        random_string = "".join(random.choice(letters) for i in range(10))
        register_data = {
            "username": "",
            "first_name": "Alanna1",
            "last_name": "Zhou1",
            "profile_pic": "",
            "social_id_token": random_string,
            "social_id_token_type": "test1",
        }
        response = self.client.post(self.REGISTER_URL, register_data)
        self.assertEqual(response.status_code, 200)
        username = json.loads(response.content)["data"]["username"]

        login_data = {"username": username, "social_id_token": random_string}
        response = self.client.post(self.LOGIN_URL, login_data)
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["data"]["auth_token"]
        return token

    def _suggest_show(self, token, suggest_data):
        self._add_friends()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.post(self.SUGGESTION_URL, suggest_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[-1]["show"]["id"], suggest_data.get("show_id"))
        self.assertEqual(data[-1]["message"], suggest_data.get("message"))

    def _send_friend_requests(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"ids": [2, 3]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        json.loads(response.content)["data"]

    def _accept_user_friend_requests(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        request_data = {"ids": [1]}
        response = self.client.post(self.FRIEND_ACCEPT_URL, request_data, format="json")
        json.loads(response.content)["data"]

    def _add_friends(self):
        self._send_friend_requests()
        self._accept_user_friend_requests(self.friend1_token)
        self._accept_user_friend_requests(self.friend2_token)

    def _check_suggestion(self, friend_token, suggest_data):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + friend_token)
        response = self.client.get(self.SUGGESTION_URL)
        data = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[-1]["show"]["id"], suggest_data.get("show_id"))
        self.assertEqual(data[-1]["message"], suggest_data.get("message"))

    def test_suggestions(self):
        suggest_data = {"users": [2, 3], "message": "Great film", "show_id": self.show.pk}
        # test if user can suggest show
        self._suggest_show(self.user_token, suggest_data)

        # test if friends can view the sent suggstion
        self._check_suggestion(self.friend1_token, suggest_data)
        self._check_suggestion(self.friend2_token, suggest_data)
