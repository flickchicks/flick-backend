import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show


class ShowCommentsTests(TestCase):
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

    def _get_comment_data_from_message(self, message):
        return {"comment_info": {"message": message, "is_spoiler": False}}

    def test_user_can_comment_show(self):
        comment_data = self._get_comment_data_from_message("Great film!")
        self._comment_show(self.user_token, comment_data)

    def _comment_show(self, token, comment_data):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.post(self.SHOW_DETAIL_URL, comment_data, format="json")
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment["message"], comment_data.get("comment_info").get("message"))

    def _send_friend_requests(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"user_ids": [2, 3]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)

    def _accept_user_friend_requests(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        request_data = {"user_ids": [1]}
        response = self.client.post(self.FRIEND_ACCEPT_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(data[0]["from_user"]["user_id"], "1")

    def _add_friends(self):
        self._send_friend_requests()
        self._accept_user_friend_requests(self.friend1_token)

    def _check_comments(self, friend1_comment):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.SHOW_DETAIL_URL)
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment["message"], friend1_comment)

    def test_friends_comments(self):
        self._add_friends()
        friend1_comment = self._get_comment_data_from_message("Love it!")
        self._comment_show(self.friend1_token, friend1_comment)
        self._check_comments("Love it!")
        friend2_comment = self._get_comment_data_from_message("It's ok")
        self._comment_show(self.friend2_token, friend2_comment)
        self._check_comments("It's ok")
