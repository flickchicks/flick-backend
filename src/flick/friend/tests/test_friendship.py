import json

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class FriendshipTests(TestCase):
    REGISTER_URL = reverse("register")
    FRIEND_LIST_URL = reverse("friend-list")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")
    FRIEND_REJECT_URL = reverse("friend-reject")
    LOGIN_URL = reverse("login")
    USERNAMES = ["alanna", "vivi", "olivia"]
    SOCIAL_ID_TOKENS = ["test1", "test2", "test3"]

    def setUp(self):
        for i, name in enumerate(self.USERNAMES):
            self._create_user(name, self.SOCIAL_ID_TOKENS[i])
            self.client = APIClient()

    def _create_user(self, username, social_id_token):
        request_data = {
            "username": username,
            "first_name": "test_user",
            "last_name": "test_user",
            "profile_pic": "",
            "social_id_token": social_id_token,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.REGISTER_URL, request_data)
        self.assertEqual(response.status_code, 200)

    def _login_user(self, username, social_id_token):
        request_data = {"username": username, "social_id_token": social_id_token}
        response = self.client.post(self.LOGIN_URL, request_data)
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["data"]["auth_token"]
        self.assertIsNotNone(token)
        return token

    def test_list_friends(self):
        token = self._login_user("alanna", "test1")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.FRIEND_LIST_URL)
        self.assertEqual(response.status_code, 200)

    def test_send_friend_request(self):
        token = self._login_user("alanna", "test1")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        request_data = {"ids": [2, 3]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_view_out_going_friend_request(self):
        token = self._login_user("alanna", "test1")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.FRIEND_REQUEST_URL)
        self.assertEqual(response.status_code, 200)

    def test_view_incoming_friend_request(self):
        token = self._login_user("vivi", "test2")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.FRIEND_ACCEPT_URL)
        self.assertEqual(response.status_code, 200)

    def test_accept_incoming_friend_request(self):
        token = self._login_user("vivi", "test2")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        request_data = {"ids": [1]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
