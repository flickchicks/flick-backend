import json

from api.tests import FlickTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient


class UserFriendsTests(FlickTestCase):
    FRIEND1_ID = 1  # friend1 and friend2 are friends
    FRIEND2_ID = 2
    USER_ID = 3  # user should see that they are friends

    FRIEND_LIST_URL = reverse("friend-list")

    def setUp(self):
        self.client = APIClient()
        self.friend1_token = self._create_user_and_login()
        self.friend2_token = self._create_user_and_login()
        self.user_token = self._create_user_and_login()

    def _friend_list_url(self, id):
        return reverse("user-friend-list", kwargs={"pk": id})

    def test_user_sees_friends_of_friend1_and_friend2(self):
        self._create_friendship(User.objects.get(id=self.FRIEND1_ID), User.objects.get(id=self.FRIEND2_ID))
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self._friend_list_url(self.FRIEND1_ID))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"][0]
        self.assertEqual(data.get("id"), self.FRIEND2_ID)

        response = self.client.get(self._friend_list_url(self.FRIEND2_ID))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"][0]
        self.assertEqual(data.get("id"), self.FRIEND1_ID)

    def test_redirects_to_friend_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self._friend_list_url(self.USER_ID))
        self.assertRedirects(
            response,
            self.FRIEND_LIST_URL,
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )
