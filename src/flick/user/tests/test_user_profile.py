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
    USER_PROFILE_URL = reverse("user-profile", kwargs={"pk": USER_ID})
    FRIEND_PROFILE_URL = reverse("user-profile", kwargs={"pk": FRIEND_ID})
    RANDO_PROFILE_URL = reverse("user-profile", kwargs={"pk": RANDO_ID})

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()
        self.rando_token = self._create_user_and_login()

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

    def _request_friendship(self, from_user, to_user):
        try:
            return Friend.objects.add_friend(from_user, to_user)
        except AlreadyFriendsError:
            return

    def _accept_friendship(self, friend_request):
        try:
            if friend_request:
                friend_request.accept()
        except AlreadyFriendsError:
            return

    def _check_friend_status(self, from_user_token, to_user_profile_url, to_user_id, friend_status):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + from_user_token)
        response = self.client.get(to_user_profile_url)
        content = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get("id"), to_user_id)
        self.assertEqual(content.get("friend_status"), friend_status)

    # Known to fail when running `python manage.py test` likely due to concurrency
    def test_view_friend_profile(self):
        from_user = User.objects.get(id=self.USER_ID)
        to_user = User.objects.get(id=self.FRIEND_ID)
        friend_request = self._request_friendship(from_user, to_user)
        self._check_friend_status(self.user_token, self.FRIEND_PROFILE_URL, self.FRIEND_ID, "outgoing request")
        self._check_friend_status(self.friend_token, self.USER_PROFILE_URL, self.USER_ID, "incoming request")
        self._accept_friendship(friend_request)
        self._check_friend_status(self.user_token, self.FRIEND_PROFILE_URL, self.FRIEND_ID, "friends")
        self._check_friend_status(self.friend_token, self.USER_PROFILE_URL, self.USER_ID, "friends")

    # Known to fail when running `python manage.py test` likely due to concurrency
    def test_view_rando_profile(self):
        from_user = User.objects.get(id=self.USER_ID)
        to_user = User.objects.get(id=self.RANDO_ID)
        Friend.objects.remove_friend(from_user, to_user)
        self._check_friend_status(self.user_token, self.RANDO_PROFILE_URL, self.RANDO_ID, "not friends")
        self._check_friend_status(self.rando_token, self.USER_PROFILE_URL, self.USER_ID, "not friends")
