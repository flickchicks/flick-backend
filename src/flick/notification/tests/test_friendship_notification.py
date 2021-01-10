import json

from api.tests import FlickTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class FriendshipNotification(FlickTestCase):
    NOTIFICATIONS_URL = reverse("notif-list")
    ME_URL = reverse("me")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()

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
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.NOTIFICATIONS_URL)
        return json.loads(response.content)["data"]

    def _check_me_has_num_notifs(self, num_notifs):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.ME_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("num_notifs"), num_notifs)

    def test_friend_request_notif_shows_once_accepted(self):
        self._send_friend_request()
        data = self._get_notification()
        self.assertEqual(len(data), 0)
        self._check_me_has_num_notifs(num_notifs=0)
        self._accept_user_friend_request()
        data = self._get_notification()[0]
        self.assertEqual(data["notif_type"], "accepted_request")
        self.assertEqual(data["from_user"]["id"], 2)
        self.assertEqual(data["to_user"]["id"], 1)
        self.assertEqual(data["friend_request_accepted"], True)
        self._check_me_has_num_notifs(num_notifs=1)
