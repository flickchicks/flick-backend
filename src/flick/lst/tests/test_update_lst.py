import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show
from tag.models import Tag


class UpdateLstTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    FRIEND_REQUEST_URL = reverse("friend-request")
    FRIEND_ACCEPT_URL = reverse("friend-accept")
    CREATE_LST_URL = reverse("lst-list")
    NOTIFICATIONS_URL = reverse("notif-list")
    UPDATE_LST_URL = reverse("lst-detail", kwargs={"pk": 5})
    ADD_TO_LST_URL = reverse("lst-detail-add", kwargs={"pk": 5})
    REMOVE_FROM_LST_URL = reverse("lst-detail-remove", kwargs={"pk": 5})

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()
        self._add_friends()

    def _create_show(self):
        show = Show()
        show.title = self._get_random_string()
        show.ext_api_id = 1
        show.ext_api_source = "tmdb"
        show.poster_pic = self._get_random_string()
        show.is_tv = True
        show.date_released = "4/1/20"
        show.status = "status"
        show.language = "en"
        show.duration = None
        show.plot = "juicy plot"
        show.seasons = 3
        show.directors = "alanna"
        show.cast = "alanna"
        show.save()
        return show

    def _get_random_string(self):
        return "".join(random.choice(string.digits) for i in range(5))

    def _get_created_show_ids(self, num_shows):
        return [self._create_show().id for n in range(num_shows)]

    def _get_created_tag_ids(self, num_tags):
        return [Tag.objects.create(name=self._get_random_string()).id for n in range(num_tags)]

    def _create_user_and_login(self):
        """Returns the auth token."""
        random_string = self._get_random_string()
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

    def _send_friend_requests(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"user_ids": [2]}
        response = self.client.post(self.FRIEND_REQUEST_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["to_user"]["user_id"], 2)

    def _accept_user_friend_requests(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        request_data = {"user_ids": [1]}
        response = self.client.post(self.FRIEND_ACCEPT_URL, request_data, format="json")
        data = json.loads(response.content)["data"]
        self.assertEqual(data[0]["from_user"]["user_id"], 1)

    def _add_friends(self):
        self._send_friend_requests()
        self._accept_user_friend_requests(self.friend_token)

    def _create_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {"name": "Alanna's Kdramas", "is_private": False, "collaborators": [], "shows": [], "tags": []}
        response = self.client.post(self.CREATE_LST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["id"], 5)
        self.assertEqual(data["is_private"], False)
        self.assertEqual(len(data["collaborators"]), 0)
        self.assertEqual(len(data["tags"]), 0)
        self.assertEqual(len(data["shows"]), 0)
        self.assertEqual(data["owner"]["user_id"], 1)

    def _update_list(self, name, is_private, collaborators, shows, tags, is_add=False, is_remove=False):
        request_data = {
            "name": name,
            "is_private": is_private,
            "collaborators": collaborators,
            "shows": shows,
            "tags": tags,
        }
        url = self.UPDATE_LST_URL
        if is_add:
            url = self.ADD_TO_LST_URL
        elif is_remove:
            url = self.REMOVE_FROM_LST_URL
        response = self.client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        return data

    def test_update_lst(self):
        self._create_list()
        show_ids = self._get_created_show_ids(num_shows=2)
        tag_ids = self._get_created_tag_ids(num_tags=2)
        name = "Updated kdramaz"
        is_private = True
        data = self._update_list(name=name, is_private=is_private, collaborators=[2], shows=show_ids, tags=tag_ids)
        self.assertEqual(data["id"], 5)
        self.assertEqual(data["name"], name)
        self.assertEqual(data["is_private"], is_private)
        self.assertEqual(len(data["collaborators"]), 1)
        self.assertEqual(len(data["shows"]), 2)
        self.assertEqual(len(data["tags"]), 2)

    def test_add_and_remove_from_lst(self):
        self._create_list()
        show_ids = self._get_created_show_ids(num_shows=2)
        tag_ids = self._get_created_tag_ids(num_tags=2)
        name = "Updated kdramaz"
        is_private = True
        data = self._update_list(
            name=name, is_private=is_private, collaborators=[2], shows=show_ids, tags=tag_ids, is_add=True
        )
        self.assertEqual(data["id"], 5)
        self.assertEqual(data["name"], name)
        self.assertEqual(data["is_private"], is_private)
        self.assertEqual(len(data["collaborators"]), 1)
        self.assertEqual(len(data["shows"]), 2)
        self.assertEqual(len(data["tags"]), 2)

        data = self._update_list(
            name=name, is_private=is_private, collaborators=[2], shows=show_ids, tags=tag_ids, is_remove=True
        )
        self.assertEqual(data["id"], 5)
        self.assertEqual(data["name"], name)
        self.assertEqual(data["is_private"], is_private)
        self.assertEqual(len(data["collaborators"]), 0)
        self.assertEqual(len(data["shows"]), 0)
        self.assertEqual(len(data["tags"]), 0)
