import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from tag.models import Tag


class SearchTagsTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    SEARCH_URL = reverse("search")

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

    def test_search_tag(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        Tag.objects.create(name="amazing")
        Tag.objects.create(name="hhhhh")
        Tag.objects.create(name="Another")
        query = "a"
        data = {"is_tag": True, "query": query}
        response = self.client.get(self.SEARCH_URL, data, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.get("success"))
        self.assertEqual(content.get("query"), query)
        data = content.get("data")
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "amazing")
        self.assertEqual(data[1]["name"], "Another")
