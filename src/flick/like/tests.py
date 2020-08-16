import json
import random
import string

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show


class LikeTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")

    def setUp(self):
        self.client = APIClient()
        self.show = self._create_show()
        self.user_token = self._create_user_and_login()
        self.SHOW_DETAIL_URL = reverse("show-detail", kwargs={"pk": self.show.pk})
        self.comment_pk = self._comment_show(self.user_token)
        self.LIKE_COMMENT_URL = reverse("like-comment", kwargs={"pk": self.comment_pk})

    def _create_show(self):
        show = Show()
        show.title = "title"
        show.ext_api_id = 1
        show.ext_api_source = "tmdb"
        show.poster_pic = "poster.pic"
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

    def _comment_show(self, token):
        comment_data = {"comment": {"message": "Great film!", "is_spoiler": False}}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.post(self.SHOW_DETAIL_URL, comment_data, format="json")
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment["message"], comment_data.get("comment").get("message"))
        return comment["id"]

    def test_like_and_cancel(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)

        # test like
        response = self.client.post(self.LIKE_COMMENT_URL)
        data = json.loads(response.content)["data"]
        likers = data["likers"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["num_likes"], 1)
        self.assertEqual(len(likers), 1)
        self.assertEqual(likers[0]["liker"]["id"], 1)

        # test cancel like
        response = self.client.post(self.LIKE_COMMENT_URL)
        data = json.loads(response.content)["data"]
        likers = data["likers"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["num_likes"], 0)
        self.assertFalse(likers)
