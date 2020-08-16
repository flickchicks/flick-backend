import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show


class ShowRatingsTests(TestCase):
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
        self._add_friends()
        self.SHOW_DETAIL_URL = reverse("show-detail", kwargs={"pk": self.show.pk})

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
            "first_name": "Alanna",
            "last_name": "Zhou",
            "profile_pic": "",
            "social_id_token": random_string,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.REGISTER_URL, register_data)
        self.assertEqual(response.status_code, 200)
        username = json.loads(response.content)["data"]["username"]

        login_data = {"username": username, "social_id_token": random_string}
        response = self.client.post(self.LOGIN_URL, login_data)
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["data"]["auth_token"]
        return token

    def test_user_can_rate_show(self):
        self._rate_show(self.user_token, 4)

    def _rate_show(self, token, rating):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        rating_data = {"user_rating": rating}
        response = self.client.post(self.SHOW_DETAIL_URL, rating_data, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["data"]["user_rating"], rating)

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

    def _check_friends_rating(self, rating):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.SHOW_DETAIL_URL)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["data"]["friends_rating"], rating)

    def test_friends_rating(self):
        friend1_rating, friend2_rating = 8, 4
        avg_rating = (friend1_rating + friend2_rating) / 2
        self._rate_show(self.friend1_token, friend1_rating)
        self._rate_show(self.friend2_token, friend2_rating)
        self._check_friends_rating(avg_rating)
