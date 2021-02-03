import json

from api.tests import FlickTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class GroupTests(FlickTestCase):
    GROUP_ID = 1
    GROUP_LIST_URL = reverse("group-list")
    UPDATE_GROUP_URL = reverse("group-detail", kwargs={"pk": GROUP_ID})
    ADD_TO_GROUP_URL = reverse("group-detail-add", kwargs={"pk": GROUP_ID})
    REMOVE_FROM_GROUP_URL = reverse("group-detail-remove", kwargs={"pk": GROUP_ID})

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.user2_token = self._create_user_and_login()
        self.user3_token = self._create_user_and_login()
        self.user4_token = self._create_user_and_login()

    def _view_groups(self, num_groups):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        response = self.client.get(self.GROUP_LIST_URL)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(len(data), num_groups)

    def _create_group(self, name="", members=[]):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {
            "name": name,
            "members": members,
        }
        response = self.client.post(self.GROUP_LIST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["name"], name)
        # a group's member count includes the group creator
        self.assertEqual(len(data["members"]), len(members) + 1)
        return data

    def _update_group(self, name="", members=[], shows=[], is_add=False, is_remove=False):
        if is_add:
            url = self.ADD_TO_GROUP_URL
        elif is_remove:
            url = self.REMOVE_FROM_GROUP_URL
        else:
            url = self.UPDATE_GROUP_URL
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {
            "name": name,
            "members": members,
            "shows": shows,
        }
        response = self.client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        return data

    def test_groups(self):
        self._view_groups(num_groups=0)

        group_name = "dummy name"
        self._create_group(name=group_name, members=[2, 3])

        self._view_groups(num_groups=1)

        new_group_name = "new dummy name"
        data = self._update_group(name=new_group_name)
        self.assertEqual(data.get("name"), new_group_name)

        new_member_id = 4
        new_show_id = self._create_show().id
        data = self._update_group(name=group_name, members=[new_member_id], shows=[new_show_id], is_add=True)
        # add to group does not modify group name
        self.assertEqual(data.get("name"), new_group_name)
        self.assertEqual(len(data.get("members")), 4)
        self.assertEqual(len(data.get("shows")), 1)

        data = self._update_group(members=[new_member_id], shows=[new_show_id], is_remove=True)
        # remove from group does not modify group name
        self.assertEqual(data.get("name"), new_group_name)
        self.assertEqual(len(data.get("members")), 3)
        self.assertEqual(len(data.get("shows")), 0)
