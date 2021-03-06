import json

from api.tests import FlickTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show


class ReadTests(FlickTestCase):
    def setUp(self):
        self.client = APIClient()
        self.show = self._create_show()
        self.user_token = self._create_user_and_login()
        self.friend1_token = self._create_user_and_login()
        self.SHOW_DETAIL_URL = reverse("show-detail", kwargs={"pk": self.show.pk})
        self.comment_pk = self._comment_show(self.user_token)
        self.READ_COMMENT_URL = reverse("read-comment", kwargs={"pk": self.comment_pk})
        self._create_friendship(user1=User.objects.get(id=1), user2=User.objects.get(id=2))

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

    def _comment_show(self, token):
        comment_data = {"comment": {"message": "spoiler content", "is_spoiler": True}}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.post(self.SHOW_DETAIL_URL, comment_data, format="json")
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment["message"], comment_data.get("comment").get("message"))
        return comment["id"]

    def _read_comment(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.post(self.READ_COMMENT_URL)
        data = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["is_readable"])

    def test_read_comment_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)

        response = self.client.get(self.SHOW_DETAIL_URL)
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(comment["is_readable"])

    def _check_before_read(self, token):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        response = self.client.get(self.SHOW_DETAIL_URL)
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(comment["is_readable"])

    def test_read_comment_by_friend(self):

        self._check_before_read(self.friend1_token)
        self._read_comment(self.friend1_token)
