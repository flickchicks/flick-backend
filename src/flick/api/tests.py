import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class FlickTests(TestCase):
    AUTHENTICATE_URL = reverse("authenticate")
    FIRST_NAME = "Alanna"
    LAST_NAME = "Zhou"

    def get_random_str(self):
        letters = string.digits
        random_string = "".join(random.choice(letters) for i in range(5))
        return random_string

    def setUp(self):
        self.client = APIClient()

    def _create_user_and_login(self):
        """Returns the auth token."""
        random_str = self.get_random_str()
        data = {
            "username": "",
            "first_name": self.FIRST_NAME,
            "last_name": self.LAST_NAME,
            "profile_pic": "",
            "social_id": random_str,
            "social_id_token": random_str,
            "social_id_token_type": "facebook",
        }
        response = self.client.post(self.AUTHENTICATE_URL, data)
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["data"]["auth_token"]
        return token
