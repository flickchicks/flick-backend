import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from friendship.models import Friend
from rest_framework.test import APIClient


class FriendshipNotification(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    CREATE_LST_URL = reverse("lst-list")
    NOTIFICATIONS_URL = reverse("notif-list")
    UPDATE_LST_URL = reverse("lst-detail", kwargs={"pk": 5})
    ME_URL = reverse("me")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()

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

    def _create_friendship(self, user1, user2):
        Friend.objects.add_friend(user1, user2).accept()

    def _send_friend_request(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"ids": [2]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["to_user"]["id"], 2)

    def _accept_user_friend_request(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)
        request_data = {"ids": [1]}
        response = self.client.post(self.FRIEND_ACCEPT_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(data[0]["from_user"]["id"], 1)

    def _get_notification(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)
        response = self.client.get(self.NOTIFICATIONS_URL)
        return json.loads(response.content)["data"]

    def _check_me_has_num_notifs(self, num_notifs):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)
        response = self.client.get(self.ME_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("num_notifs"), num_notifs)

    def test_friend_request_notif_shows_once_accepted(self):
        self._check_me_has_num_notifs(num_notifs=0)
        self._send_friend_request()
        data = self._get_notification()
        self.assertEqual(len(data), 0)
        self._check_me_has_num_notifs(num_notifs=0)
        self._accept_user_friend_request()
        data = self._get_notification()[0]
        self.assertEqual(data["notif_type"], "friend_request")
        self.assertEqual(data["from_user"]["id"], 1)
        self.assertEqual(data["to_user"]["id"], 2)
        self.assertEqual(data["friend_request_accepted"], True)
        self._check_me_has_num_notifs(num_notifs=1)
