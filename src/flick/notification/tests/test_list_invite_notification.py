import json
import random
import string

from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show


class ListInviteNotificationTests(TransactionTestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")
    CREATE_LST_URL = reverse("lst-list")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()
        self._add_friends()

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

    def _send_friend_requests(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"user_ids": [2]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["to_user"]["user_id"], "2")

    def _accept_user_friend_requests(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        request_data = {"user_ids": [1]}
        response = self.client.post(self.FRIEND_ACCEPT_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(data[0]["from_user"]["user_id"], "1")

    def _add_friends(self):
        self._send_friend_requests()
        self._accept_user_friend_requests(self.friend_token)

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

    def _create_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {
            "lst_name": "Alanna's Kdramas",
            "collaborators": [2],
            "shows": [self._create_show().id],
            "tags": [],
        }
        response = self.client.post(self.CREATE_LST_URL, request_data, format="json")
        print(response)
        self.assertEqual(response.status_code, 200)

    def test_list_invite_via_list_creation(self):
        # user adds a friend
        # user creates a list, adds collaborator with friend
        # login as the collaborator
        # collaborator should have the notification from the user
        self._create_list()
        # self.assertTrue(True)

    # def test_list_invite_via_list_update(self):
    #     self.assertTrue(True)
