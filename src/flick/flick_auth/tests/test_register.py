import json

from django.test import TestCase
from django.urls import reverse


class RegisterTests(TestCase):

    REGISTER_URL = reverse("register")

    def test_register(self):
        request_data = {
            "username": "alanna",
            "first_name": "Alanna",
            "last_name": "Zhou",
            "profile_pic": "",
            "social_id_token": "test",
            "social_id_token_type": "test",
        }
        response = self.client.post(self.REGISTER_URL, request_data)
        self.assertEqual(response.status_code, 200)

    def test_username_is_generated(self):
        request_data = {
            "username": "",
            "first_name": "Alanna",
            "last_name": "Zhou",
            "profile_pic": "",
            "social_id_token": "test",
            "social_id_token_type": "test",
        }
        response = self.client.post(self.REGISTER_URL, request_data)
        self.assertEqual(response.status_code, 200)
        username = json.loads(response.content)["data"]["username"]
        self.assertEqual(username, "AlannaZhou")

    def test_missing_social_id_token(self):
        request_data = {
            "username": "alanna",
            "first_name": "Alanna",
            "last_name": "Zhou",
            "profile_pic": "",
            "social_id_token": "",
            "social_id_token_type": "test",
        }
        with self.assertRaises(Exception):
            response = self.client.post(self.REGISTER_URL, request_data)
            self.assertEqual(response.status_code, 404)
