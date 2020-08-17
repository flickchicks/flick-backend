import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class ListInviteNotificationTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")
    CREATE_LST_URL = reverse("lst-list")
    NOTIFICATIONS_URL = reverse("notif-list")
    UPDATE_LST_URL = reverse("lst-detail", kwargs={"pk": 5})
    ME_URL = reverse("me")

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
        request_data = {"ids": [2]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["to_user"]["id"], 2)

    def _accept_user_friend_requests(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        request_data = {"ids": [1]}
        response = self.client.post(self.FRIEND_ACCEPT_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(data[0]["from_user"]["id"], 1)

    def _add_friends(self):
        self._send_friend_requests()
        self._accept_user_friend_requests(self.friend_token)

    def _create_list(self, id=5):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"name": "Alanna's Kdramas", "collaborators": [2], "shows": [], "tags": []}
        response = self.client.post(self.CREATE_LST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        # each user gets 2 default lists, additional one will have id of 5
        self.assertEqual(data["id"], id)
        self.assertEqual(data["collaborators"][0]["id"], 2)
        self.assertEqual(data["owner"]["id"], 1)
        return data["id"]

    def _create_and_update_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"name": "Alanna's Kdramas", "collaborators": [], "shows": [], "tags": []}
        response = self.client.post(self.CREATE_LST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        # each user gets 2 default lists, additional one will have id of 5
        self.assertEqual(data["id"], 5)
        self.assertEqual(len(data["collaborators"]), 0)
        self.assertEqual(data["owner"]["id"], 1)

        request_data = {"name": "Alanna's Kdramas", "collaborators": [2], "shows": [], "tags": []}
        response = self.client.post(self.UPDATE_LST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["id"], 5)
        self.assertEqual(data["collaborators"][0]["id"], 2)
        self.assertEqual(data["owner"]["id"], 1)

    def _check_notification(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)
        response = self.client.get(self.NOTIFICATIONS_URL)
        data = json.loads(response.content)["data"][0]
        self.assertEqual(data["notif_type"], "list_invite")
        self.assertEqual(data["from_user"]["id"], 1)
        self.assertEqual(data["to_user"]["id"], 2)
        self.assertEqual(data["lst"]["id"], 5)

    def _check_me_has_num_notifs(self, num_notifs):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)
        response = self.client.get(self.ME_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("num_notifs"), num_notifs)

    def test_list_invite_via_list_creation(self):
        self._check_me_has_num_notifs(num_notifs=0)
        self._create_list()
        self._check_notification()
        self._check_me_has_num_notifs(num_notifs=1)

    def test_list_invite_via_list_update(self):
        self._create_and_update_list()
        self._check_notification()
        self._check_me_has_num_notifs(num_notifs=1)
