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

    def _get_notification(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.NOTIFICATIONS_URL)
        return json.loads(response.content)["data"]

    def _check_me_has_num_notifs(self, num_notifs, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(self.ME_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("num_notifs"), num_notifs)

    def test_incoming_friend_request_accepted(self):
        # user 1 sends friend request to user 2
        self._send_friend_request()

        # notifications only appear when requests have been accepted
        # so, so far no notifications yet on either side
        data = self._get_notification(self.user_token)
        self.assertEqual(len(data), 0)
        data = self._get_notification(self.friend_token)
        self.assertEqual(len(data), 0)
        self._check_me_has_num_notifs(num_notifs=0, token=self.user_token)
        self._check_me_has_num_notifs(num_notifs=0, token=self.friend_token)

        # user 2 accepts friend request from user 1
        self._accept_user_friend_request()

        # user 1 checks notifications
        data = self._get_notification(self.user_token)[0]
        self.assertEqual(data["notif_type"], "outgoing_friend_request_accepted")
        self.assertEqual(data["from_user"]["id"], 2)
        self.assertEqual(data["to_user"]["id"], 1)
        self._check_me_has_num_notifs(num_notifs=1, token=self.user_token)

        # user 2 checks notifications
        data = self._get_notification(self.friend_token)[0]
        self.assertEqual(data["notif_type"], "incoming_friend_request_accepted")
        self.assertEqual(data["from_user"]["id"], 1)
        self.assertEqual(data["to_user"]["id"], 2)
        self._check_me_has_num_notifs(num_notifs=1, token=self.friend_token)
