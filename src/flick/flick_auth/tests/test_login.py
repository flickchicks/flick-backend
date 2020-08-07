import json

from django.test import TestCase
from django.urls import reverse


class LoginTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    USERNAME = "alanna"
    SOCIAL_ID_TOKEN = "test"

    def setUp(self):
        self._create_user()

    def _create_user(self):
        request_data = {
            "username": self.USERNAME,
            "first_name": "Alanna",
            "last_name": "Zhou",
            "profile_pic": "",
            "social_id_token": self.SOCIAL_ID_TOKEN,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.REGISTER_URL, request_data)
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        request_data = {"username": self.USERNAME, "social_id_token": self.SOCIAL_ID_TOKEN}
        response = self.client.post(self.LOGIN_URL, request_data)
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["data"]["auth_token"]
        self.assertIsNotNone(token)

    def test_invalid_login(self):
        request_data = {"username": self.USERNAME + "x", "social_id_token": self.SOCIAL_ID_TOKEN}
        response = self.client.post(self.LOGIN_URL, request_data)
        self.assertEqual(response.status_code, 404)
