import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class MeTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    ME_URL = reverse("me")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()

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

    def test_me(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.ME_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("id"), 1)
        self.assertEqual(content.get("username"), "AlannaZhou")
        self.assertEqual(content.get("first_name"), "Alanna")
        self.assertEqual(content.get("last_name"), "Zhou")
        self.assertEqual(len(content.get("owner_lsts")), 2)
        self.assertEqual(len(content.get("collab_lsts")), 0)
