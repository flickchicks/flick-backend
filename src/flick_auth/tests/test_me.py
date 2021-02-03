import json

from api.tests import FlickTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class MeTests(FlickTestCase):
    ME_URL = reverse("me")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()

    def test_me(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.ME_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data.get("id"), 1)
        self.assertEqual(data.get("username"), self.NAME.replace(" ", ""))
        self.assertEqual(data.get("name"), self.NAME)
        self.assertEqual(data.get("num_notifs"), 0)
        self.assertEqual(len(data.get("owner_lsts")), 2)
        self.assertEqual(len(data.get("collab_lsts")), 0)

    def test_update_me_empty_fields_except_username_ok(self):
        bio = "Updating my bio!"
        phone_number = "21234234"
        request_data = {
            "bio": bio,
            "phone_number": phone_number,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.post(self.ME_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data.get("id"), 1)
        self.assertEqual(data.get("username"), self.NAME.replace(" ", ""))
        self.assertEqual(data.get("name"), self.NAME)
        self.assertEqual(data.get("bio"), bio)
        self.assertEqual(data.get("phone_number"), phone_number)
        self.assertEqual(data.get("num_notifs"), 0)
        self.assertEqual(len(data.get("owner_lsts")), 2)
        self.assertEqual(len(data.get("collab_lsts")), 0)

        request_data = {
            "name": "",
            "bio": "",
            "phone_number": "",
            "social_id": "",
            "social_id_token_type": "",
            "social_id_token": "",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.post(self.ME_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data.get("id"), 1)
        self.assertEqual(data.get("username"), self.NAME.replace(" ", ""))
        self.assertEqual(data.get("name"), "")
        self.assertEqual(data.get("bio"), "")
        self.assertEqual(data.get("name"), "")
        self.assertEqual(data.get("phone_number"), "")
        self.assertEqual(data.get("social_id"), "")
        self.assertEqual(data.get("social_id_token_type"), "")
        self.assertEqual(data.get("social_id_token"), "")
        self.assertEqual(data.get("num_notifs"), 0)
        self.assertEqual(len(data.get("owner_lsts")), 2)
        self.assertEqual(len(data.get("collab_lsts")), 0)

    def test_update_me_empty_username_fails(self):
        request_data = {
            "username": "",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.post(self.ME_URL, request_data, format="json")
        self.assertEqual(response.status_code, 404)
        error = json.loads(response.content)["error"]
        self.assertEqual(error, "Username must be between 3 and 30 characters.")
