import json

from api.tests import FlickTransactionTestCase
from django.test import tag
from django.urls import reverse
from rest_framework.test import APIClient


class DiscoverTests(FlickTransactionTestCase):
    DISCOVER_URL = reverse("discover")

    def setUp(self):
        self.client = APIClient()

    @tag("flakey")
    def test_search_show(self):
        response = self.client.get(self.DISCOVER_URL, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.get("success"))
        data = content.get("data")
        self.assertEqual(len(data["trending_movies"]), 5)
        self.assertEqual(len(data["trending_tvs"]), 5)
        self.assertEqual(len(data["trending_animes"]), 5)
