import json

from django.test import TestCase
from django.urls import reverse


class FriendshipTests(TestCase):
    REGISTER_URL = reverse("register")
    FRIEND_LIST_URL = reverse("friend-list")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")
    FRIEND_REJECT_URL = reverse("friend-reject")
    LOGIN_URL = reverse("login")
    BASE64_IMAGE = "data:image/png;base64,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"
    USERNAMES = ["alanna", "vivi", "olivia"]
    SOCIAL_ID_TOKENS = ["test1", "test2", "test3"]

    def setUp(self):
        for i, name in enumerate(self.USERNAMES):
            self._create_user(name, self.SOCIAL_ID_TOKENS[i])

    def _create_user(self, username, social_id_token):
        request_data = {
            "username": username,
            "first_name": "test_user",
            "last_name": "test_user",
            "profile_pic": self.BASE64_IMAGE,
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
        auth_headers = {"HTTP_AUTHORIZATION": "token " + token}
        response = self.client.get(self.FRIEND_LIST_URL, **auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_send_friend_request(self):
        token = self._login_user("alanna", "test1")
        auth_headers = {"HTTP_AUTHORIZATION": "token " + token}
        request_data = {
            "user_ids": [2, 3],
        }
        response = self.client.post(
            self.FRIEND_REQUEST_URL, request_data, content_type="application/json", **auth_headers
        )
        self.assertEqual(response.status_code, 200)

    def test_view_out_going_friend_request(self):
        token = self._login_user("alanna", "test1")
        auth_headers = {"HTTP_AUTHORIZATION": "token " + token}
        response = self.client.get(self.FRIEND_REQUEST_URL, **auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_view_incoming_friend_request(self):
        token = self._login_user("vivi", "test2")
        auth_headers = {"HTTP_AUTHORIZATION": "token " + token}
        response = self.client.get(self.FRIEND_ACCEPT_URL, **auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_accept_incoming_friend_request(self):
        token = self._login_user("vivi", "test2")
        auth_headers = {"HTTP_AUTHORIZATION": "token " + token}
        request_data = {
            "user_ids": [1],
        }
        response = self.client.post(
            self.FRIEND_ACCEPT_URL, request_data, content_type="application/json", **auth_headers
        )
        self.assertEqual(response.status_code, 200)
