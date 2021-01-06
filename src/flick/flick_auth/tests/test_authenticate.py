import json

from api.tests import FlickTestCase
from rest_framework.test import APIClient


class AuthenticateTests(FlickTestCase):
    def setUp(self):
        self.client = APIClient()

    def _check_logged_in_or_registered(self, user_data, check_user_data):
        response = self.client.post(self.AUTHENTICATE_URL, user_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["username"], check_user_data.get("username"))
        self.assertEqual(data["name"], check_user_data.get("name"))
        self.assertEqual(data["profile_pic"], check_user_data.get("profile_pic"))
        self.assertEqual(data["social_id"], check_user_data.get("social_id"))
        self.assertEqual(data["social_id_token"], check_user_data.get("social_id_token"))
        self.assertEqual(data["social_id_token_type"], check_user_data.get("social_id_token_type"))
        return data.get("auth_token")

    def test_authenticate(self):
        random_str = self.get_random_str()
        user_data = {
            "username": "",
            "name": self.NAME,
            "profile_pic": "",
            "social_id": random_str,
            "social_id_token": random_str,
            "social_id_token_type": "test",
        }
        check_user_data = user_data
        check_user_data["username"] = self.NAME.replace(" ", "")
        # Registers the first time, get the token
        first_token = self._check_logged_in_or_registered(user_data, check_user_data)
        # Logs in the second time, get the token
        second_token = self._check_logged_in_or_registered(user_data, check_user_data)
        self.assertEqual(first_token, second_token)

        # Should continue to be able to log in with only the three necessary fields
        user_data = {
            "social_id": random_str,
            "social_id_token": random_str,
            "social_id_token_type": "test",
        }
        token = self._check_logged_in_or_registered(user_data, check_user_data)
        self.assertEqual(first_token, token)

        # Even if the user sends in different data, we still log in the same person
        user_data = {
            "name": "dummyname",
            "username": "dummyusername",
            "social_id": random_str,
            "social_id_token": random_str,
            "social_id_token_type": "test",
        }
        self._check_logged_in_or_registered(user_data, check_user_data)
        self.assertEqual(first_token, token)

    def test_must_supply_name_if_missing_username(self):
        random_str = self.get_random_str()
        user_data = {
            "profile_pic": "",
            "social_id": random_str,
            "social_id_token": random_str,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.AUTHENTICATE_URL, user_data)
        self.assertEqual(response.status_code, 404)
        error = json.loads(response.content)["error"]
        self.assertEqual(error, "Must supply a name to get a generated username.")

    def test_no_name_ok(self):
        random_str = self.get_random_str()
        user_data = {
            "username": "randomusername",
            "profile_pic": "",
            "social_id": random_str,
            "social_id_token": random_str,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.AUTHENTICATE_URL, user_data)
        self.assertEqual(response.status_code, 200)

    def test_username_taken(self):
        random_str = self.get_random_str()
        user_data = {
            "username": self.NAME,
            "profile_pic": "",
            "social_id": random_str,
            "social_id_token": random_str,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.AUTHENTICATE_URL, user_data)
        self.assertEqual(response.status_code, 200)

        random_str = self.get_random_str()
        user_data = {
            "username": self.NAME,
            "profile_pic": "",
            "social_id": random_str,
            "social_id_token": random_str,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.AUTHENTICATE_URL, user_data)
        self.assertEqual(response.status_code, 404)
        error = json.loads(response.content)["error"]
        self.assertEqual(error, f"Profile already exists with the username {self.NAME}.")

    def test_diff_social_id_but_social_id_token_taken(self):
        social_id_token = self.get_random_str()
        user_data = {
            "username": self.NAME,
            "profile_pic": "",
            "social_id": self.get_random_str(),
            "social_id_token": social_id_token,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.AUTHENTICATE_URL, user_data)
        self.assertEqual(response.status_code, 200)

        user_data = {
            "username": self.NAME,
            "profile_pic": "",
            "social_id": self.get_random_str(),
            "social_id_token": social_id_token,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.AUTHENTICATE_URL, user_data)
        self.assertEqual(response.status_code, 404)
        error = json.loads(response.content)["error"]
        self.assertEqual(error, f"Profile already exists with the social_id_token {social_id_token}.")
