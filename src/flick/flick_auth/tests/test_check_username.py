from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CheckUsernameTests(TestCase):
    CHECK_USERNAME_URL = reverse("check-username")

    def setUp(self):
        User.objects.create(username="alanna", first_name="Alanna", last_name="Zhou")

    def test_username_availability(self):
        data = {"username": "alanna_zhou"}
        response = self.client.post(self.CHECK_USERNAME_URL, data)
        self.assertEqual(response.status_code, 200)

        data = {"username": "alanna"}
        response = self.client.post(self.CHECK_USERNAME_URL, data)
        self.assertEqual(response.status_code, 404)

    def test_username_30_char_limit(self):
        data = {"username": "alannaalannaalannaalannaalanna"}
        response = self.client.post(self.CHECK_USERNAME_URL, data)
        self.assertEqual(response.status_code, 200)

        data = {"username": "alannaalannaalannaalannaalannaX"}
        response = self.client.post(self.CHECK_USERNAME_URL, data)
        self.assertEqual(response.status_code, 404)
