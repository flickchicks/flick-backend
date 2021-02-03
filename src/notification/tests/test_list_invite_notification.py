import json

from api.tests import FlickTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient


class ListInviteNotificationTests(FlickTestCase):
    CREATE_LST_URL = reverse("lst-list")
    NOTIFICATIONS_URL = reverse("notif-list")
    ADD_TO_LST_URL = reverse("lst-detail-add", kwargs={"pk": 5})
    ME_URL = reverse("me")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()
        self._create_friendship(user1=User.objects.get(id=1), user2=User.objects.get(id=2))

    def _create_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"name": "Alanna's Kdramas", "collaborators": [2], "shows": [], "tags": []}
        response = self.client.post(self.CREATE_LST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        # each user gets 2 default lists, additional one will have id of 5
        self.assertEqual(data["id"], 5)
        self.assertEqual(data["collaborators"][0]["id"], 2)
        self.assertEqual(data["owner"]["id"], 1)

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
        response = self.client.post(self.ADD_TO_LST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["id"], 5)
        self.assertEqual(data["collaborators"][0]["id"], 2)
        self.assertEqual(data["owner"]["id"], 1)

    def _check_notification(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)
        response = self.client.get(self.NOTIFICATIONS_URL)
        data = json.loads(response.content)["data"]
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
