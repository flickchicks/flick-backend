import json

from api.tests import FlickTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class MeTests(FlickTestCase):
    ME_URL = reverse("me")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()

    def test_me(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.ME_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("id"), 1)
        self.assertEqual(content.get("username"), self.NAME.replace(" ", ""))
        self.assertEqual(content.get("name"), self.NAME)
        self.assertEqual(content.get("num_notifs"), 0)
        self.assertEqual(len(content.get("owner_lsts")), 2)
        self.assertEqual(len(content.get("collab_lsts")), 0)
