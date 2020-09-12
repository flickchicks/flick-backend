import json

from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class SearchShowsTests(TransactionTestCase):
    DISCOVER_URL = reverse("discover-show")

    def setUp(self):
        self.client = APIClient()

    def test_search_show(self):
        response = self.client.get(self.DISCOVER_URL, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.get("success"))
        data = content.get("data")
        self.assertEqual(len(data["trending_movies"]), 5)
        self.assertEqual(len(data["trending_tvs"]), 5)
        self.assertEqual(len(data["trending_animes"]), 5)
