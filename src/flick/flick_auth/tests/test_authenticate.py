import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class AuthenticateTests(TestCase):
    AUTHENTICATE_URL = reverse("authenticate")

    def setUp(self):
        self.client = APIClient()

    def _check_logged_in_or_registered(self, data):
        response = self.client.post(self.AUTHENTICATE_URL, data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["username"], data.get("username"))
        self.assertEqual(data["first_name"], data.get("first_name"))
        self.assertEqual(data["last_name"], data.get("last_name"))
        self.assertEqual(data["profile_pic"], data.get("profile_pic"))
        self.assertEqual(data["social_id"], data.get("social_id"))
        self.assertEqual(data["social_id_token"], data.get("social_id_token"))
        self.assertEqual(data["social_id_token_type"], data.get("social_id_token_type"))

    def test_authenticate(self):
        letters = string.digits
        random_string = "".join(random.choice(letters) for i in range(10))
        data = {
            "username": "",
            "first_name": "Alanna",
            "last_name": "Zhou",
            "profile_pic": "",
            "social_id": random_string,
            "social_id_token": random_string,
            "social_id_token_type": "test",
        }
        self._check_logged_in_or_registered(data)

        # doing this again should return the same data
        self._check_logged_in_or_registered(data)
