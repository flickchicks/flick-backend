import json

from api.tests import FlickTransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class SearchShowsTests(FlickTransactionTestCase):
    SEARCH_URL = reverse("search")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()

    def test_search_show(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        query = "Maleficent"
        data = {"is_movie": True, "query": query}
        response = self.client.get(self.SEARCH_URL, data, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.get("success"))
        self.assertEqual(content.get("query"), query)
        data = content.get("data")[0]
        self.assertIn("id", data)
        self.assertIn("backdrop_pic", data)
        self.assertIn("date_released", data)
        self.assertIn("ext_api_id", data)
        self.assertIn("ext_api_source", data)
        self.assertIn("is_adult", data)
        self.assertIn("is_tv", data)
        self.assertIn("language", data)
        self.assertIn("plot", data)
        self.assertIn("poster_pic", data)
        self.assertIn("title", data)
