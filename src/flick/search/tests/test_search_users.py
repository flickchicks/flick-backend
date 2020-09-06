import json
import random
import string

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from friendship.exceptions import AlreadyFriendsError
from friendship.models import Friend
from rest_framework.test import APIClient


class SearchUsersTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
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
        self.friend3 = User.objects.get(id=4)
        # user and friend3 should have one mutual friend: friend1
        self._create_friendship(user1=self.user, user2=self.friend1)
        self._create_friendship(user1=self.user, user2=self.friend2)
        self._create_friendship(user1=self.friend3, user2=self.friend1)

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

    def _create_friendship(self, user1, user2):
        try:
            Friend.objects.add_friend(user1, user2).accept()
        except AlreadyFriendsError:
            return

    def test_search_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        data = {"is_user": True, "query": self.friend3.username}
        response = self.client.get(self.SEARCH_URL, data, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.get("success"))
        data = content.get("data")[0]
        self.assertEqual(data["id"], self.friend3.id)
        self.assertEqual(data["username"], self.friend3.username)
        self.assertEqual(data["first_name"], self.friend3.first_name)
        self.assertEqual(data["last_name"], self.friend3.last_name)
        self.assertEqual(data["num_mutual_friends"], 1)
