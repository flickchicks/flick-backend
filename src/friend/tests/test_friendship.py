from api.tests import FlickTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class FriendshipTests(FlickTestCase):
    FRIEND_LIST_URL = reverse("friend-list")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")
    FRIEND_REJECT_URL = reverse("friend-reject")
    VALID_USER_PROFILE_URL = reverse("user-profile", kwargs={"pk": 2})
    REQUEST_USER_PROFILE_URL = reverse("user-profile", kwargs={"pk": 1})
    INVALID_USER_PROFILE_URL = reverse("user-profile", kwargs={"pk": 10})
    ME_URL = reverse("me")

    def setUp(self):
        self.client = APIClient()
        self.user1_token = self._create_user_and_login()
        self.user2_token = self._create_user_and_login()
        self.user3_token = self._create_user_and_login()

    def test_list_friends(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.get(self.FRIEND_LIST_URL)
        self.assertEqual(response.status_code, 200)

    def test_send_friend_request(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        request_data = {"ids": [2, 3]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_view_out_going_friend_request(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.get(self.FRIEND_REQUEST_URL)
        self.assertEqual(response.status_code, 200)

    def test_view_incoming_friend_request(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user2_token)
        response = self.client.get(self.FRIEND_ACCEPT_URL)
        self.assertEqual(response.status_code, 200)

    def test_accept_incoming_friend_request(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user2_token)
        request_data = {"ids": [1]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_user_profile_exists(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.get(self.VALID_USER_PROFILE_URL)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.get(self.INVALID_USER_PROFILE_URL)
        self.assertEqual(response.status_code, 404)

    def test_redirect(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user1_token)
        response = self.client.get(self.REQUEST_USER_PROFILE_URL)
        self.assertRedirects(response, self.ME_URL)
