import json
import random
import string

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from friendship.exceptions import AlreadyFriendsError
from friendship.models import Friend
from rest_framework.test import APIClient


class UserProfileTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    ME_URL = reverse("me")
    USER_ID = 1
    FRIEND_ID = 2
    RANDO_ID = 3
    FRIEND_PROFILE_URL = reverse("user-profile", kwargs={"pk": FRIEND_ID})
    RANDO_PROFILE_URL = reverse("user-profile", kwargs={"pk": RANDO_ID})

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()
        self.rando_token = self._create_user_and_login()
        self._create_friendship(user1=User.objects.get(id=self.USER_ID), user2=User.objects.get(id=self.FRIEND_ID))

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

    def test_view_friend_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.FRIEND_PROFILE_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("id"), self.FRIEND_ID)
        self.assertTrue(content.get("is_friend"))

    def test_view_rando_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.RANDO_PROFILE_URL)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("id"), self.RANDO_ID)
        self.assertFalse(content.get("is_friend"))
