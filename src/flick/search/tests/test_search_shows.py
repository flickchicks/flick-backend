import json
import random
import string

from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class SearchShowsTests(TransactionTestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.SEARCH_URL = reverse("search")

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

    def test_search_show(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        data = {"is_movie": True, "query": "Maleficent"}
        response = self.client.get(self.SEARCH_URL, data, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.get("success"))
        data = content.get("data")[0]
        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertIn("poster_pic", data)
        self.assertIn("is_tv", data)
        self.assertIn("plot", data)
        self.assertIn("date_released", data)
        self.assertIn("status", data)
        self.assertIn("language", data)
        self.assertIn("duration", data)
        self.assertIn("seasons", data)
        self.assertIn("audience_level", data)
        self.assertIn("keywords", data)
