import json
from user.models import Profile

from api.tests import FlickTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from show.models import Show
from suggestion.models import PrivateSuggestion


class LikeTests(FlickTestCase):
    def setUp(self):
        self.client = APIClient()
        self.show = self._create_show()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()
        self.user = User.objects.get(id=1)
        self.friend = User.objects.get(id=2)
        self._create_friendship(user1=self.user, user2=self.friend)
        self.suggestion_pk = self._suggest_show()
        self.SHOW_DETAIL_URL = reverse("show-detail", kwargs={"pk": self.show.pk})
        self.SUGGEST_URL = reverse("private-suggestion")
        self.SUGGESTION_URL = reverse("private-suggestion-list")
        self.NOTIFICATION_URL = reverse("notif-list")
        self.comment_pk = self._comment_show(self.user_token)
        self.LIKE_COMMENT_URL = reverse("like-comment", kwargs={"pk": self.comment_pk})
        self.LIKE_LST_URL = reverse("like-list", kwargs={"pk": 1})
        self.LIKE_SUGGESTION_URL = reverse("like-private-suggestion", kwargs={"pk": self.suggestion_pk})

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
        comment_data = {"comment": {"message": "Great film!", "is_spoiler": False}}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.post(self.SHOW_DETAIL_URL, comment_data, format="json")
        comment = json.loads(response.content)["data"]["comments"][-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment["message"], comment_data.get("comment").get("message"))
        return comment["id"]

    def _suggest_show(self):
        pri_suggestion = PrivateSuggestion()
        pri_suggestion.from_user = Profile.objects.get(user=self.user)
        pri_suggestion.to_user = Profile.objects.get(user=self.friend)
        pri_suggestion.show = self.show
        pri_suggestion.message = "good show"
        pri_suggestion.save()
        return pri_suggestion.id

    def test_like_and_cancel(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)

        # test like
        response = self.client.post(self.LIKE_COMMENT_URL)
        data = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["num_likes"], 1)
        self.assertTrue(data["has_liked"])

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)

        # test notification is recieved
        response = self.client.get(self.NOTIFICATION_URL)
        data = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        notification = data[0]
        self.assertEqual(notification["from_user"]["id"], 2)
        self.assertEqual(notification["to_user"]["id"], 1)
        self.assertEqual(notification["notif_type"], "comment_like")

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)

        # test cancel like
        response = self.client.post(self.LIKE_COMMENT_URL)
        data = json.loads(response.content)["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["num_likes"], 0)
        self.assertFalse(data["has_liked"])

    def test_lst_like_and_cancel(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)

        # test like
        response = self.client.post(self.LIKE_LST_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["num_likes"], 1)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)

        # test notification is received
        response = self.client.get(self.NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(len(data), 1)
        notification = data[0]
        self.assertEqual(notification["from_user"]["id"], 2)
        self.assertEqual(notification["to_user"]["id"], 1)
        self.assertEqual(notification["notif_type"], "list_like")

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)

        # test cancel like
        response = self.client.post(self.LIKE_LST_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["num_likes"], 0)

    def test_suggestion_like_and_cancel(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)

        # test like
        response = self.client.post(self.LIKE_SUGGESTION_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertTrue(data["has_liked"])

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)

        # test notification is received
        response = self.client.get(self.NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(len(data), 1)
        notification = data[0]
        self.assertEqual(notification["from_user"]["id"], 2)
        self.assertEqual(notification["to_user"]["id"], 1)
        self.assertEqual(notification["notif_type"], "suggestion_like")

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)

        # test cancel like
        response = self.client.post(self.LIKE_SUGGESTION_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertFalse(data["has_liked"])
