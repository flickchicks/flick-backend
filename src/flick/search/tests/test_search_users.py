import json

from api.tests import FlickTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient


class SearchUsersTests(FlickTestCase):
    SEARCH_URL = reverse("search")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend1_token = self._create_user_and_login()
        self.friend2_token = self._create_user_and_login()
        self.friend3_token = self._create_user_and_login()
        self.user = User.objects.get(id=1)
        self.friend1 = User.objects.get(id=2)
        self.friend2 = User.objects.get(id=3)
        # user and friend3 should have one mutual friend: friend1
        self.friend3 = User.objects.get(id=4)

    # Known to fail when running `python manage.py test` likely due to concurrency
    def test_search_user(self):
        self._create_friendship(user1=self.user, user2=self.friend1)
        self._create_friendship(user1=self.user, user2=self.friend2)
        self._create_friendship(user1=self.friend3, user2=self.friend1)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        data = {"is_user": True, "query": self.friend3.username}
        response = self.client.get(self.SEARCH_URL, data, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.get("success"))
        self.assertEqual(content.get("query"), self.friend3.username)
        data = content.get("data")[0]
        self.assertEqual(data["id"], self.friend3.id)
        self.assertEqual(data["username"], self.friend3.username)
        self.assertEqual(data["name"], self.friend3.first_name)
        self.assertEqual(data["num_mutual_friends"], 1)
