import json

from api.tests import FlickTestCase
from django.contrib.auth.models import User
from django.test import tag
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show


class ShowRatingsAndCommentTests(FlickTestCase):
    def setUp(self):
        self.client = APIClient()
        self.show = self._create_show()
        self.user_token = self._create_user_and_login()
        self.friend1_token = self._create_user_and_login()
        self.friend2_token = self._create_user_and_login()
        self.SHOW_DETAIL_URL = reverse("show-detail", kwargs={"pk": self.show.pk})
        self._create_friendship(user1=User.objects.get(id=1), user2=User.objects.get(id=2))
        self._create_friendship(user1=User.objects.get(id=1), user2=User.objects.get(id=3))

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

    def test_user_can_rate_show(self):
        self._rate_show(self.user_token, 4)
        self._rate_show(self.user_token, 5)

    def _rate_show(self, token, rating):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        rating_data = {"user_rating": rating}
        response = self.client.post(self.SHOW_DETAIL_URL, rating_data, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["data"]["user_rating"], rating)

    def _get_comment_data_from_message(self, message):
        return {"comment": {"message": message, "is_spoiler": False}}

    def test_user_can_comment_show(self):
        comment_data = self._get_comment_data_from_message("Great film!")
        self._comment_show(self.user_token, comment_data)

    def _comment_show(self, token, comment_data):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.post(self.SHOW_DETAIL_URL, comment_data, format="json")
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment["message"], comment_data.get("comment").get("message"))

    def _check_friends_rating(self, rating):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.SHOW_DETAIL_URL)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["data"]["friends_rating"], rating)

    # Known to fail when running `python manage.py test` likely due to concurrency
    @tag("flakey")
    def test_friends_rating(self):
        friend1_rating, friend2_rating = 8, 4
        avg_rating = (friend1_rating + friend2_rating) / 2
        self._rate_show(self.friend1_token, friend1_rating)
        self._rate_show(self.friend2_token, friend2_rating)
        self._check_friends_rating(avg_rating)

    def _check_comments(self, friend_comment):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.SHOW_DETAIL_URL)
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment["message"], friend_comment)

    def test_friends_comments(self):
        friend1_comment = self._get_comment_data_from_message("Love it!")
        self._comment_show(self.friend1_token, friend1_comment)
        self._check_comments("Love it!")
        friend2_comment = self._get_comment_data_from_message("It's ok")
        self._comment_show(self.friend2_token, friend2_comment)
        self._check_comments("It's ok")
