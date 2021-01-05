import json

from api.tests import FlickTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from tag.models import Tag


class SearchTagsTests(FlickTestCase):
    SEARCH_URL = reverse("search")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()

    def test_search_tag(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        Tag.objects.create(name="amazing")
        Tag.objects.create(name="hhhhh")
        Tag.objects.create(name="Another")
        query = "a"
        data = {"is_tag": True, "query": query}
        response = self.client.get(self.SEARCH_URL, data, format="json")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.get("success"))
        self.assertEqual(content.get("query"), query)
        data = content.get("data")
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "amazing")
        self.assertEqual(data[1]["name"], "Another")
