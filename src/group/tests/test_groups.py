import json

from api.tests import FlickTestCase
from django.urls import reverse
from rest_framework.test import APIClient


class GroupTests(FlickTestCase):
    GROUP_LIST_URL = reverse("group-list")

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.user2_token = self._create_user_and_login()
        self.user3_token = self._create_user_and_login()
        self.user4_token = self._create_user_and_login()
        self._view_groups(num_groups=0)
        self.GROUP_NAME = "dummy name"
        self._create_group(name=self.GROUP_NAME, members=[2, 3])

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

    def _view_group_detail(self, user_token, group_id=1):
        url = reverse("group-detail", kwargs={"pk": group_id})
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user_token)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        return data

    def _update_group(self, group_id=1, name="", members=[], shows=[], is_add=False, is_remove=False):
        if is_add:
            url = reverse("group-detail-add", kwargs={"pk": group_id})
        elif is_remove:
            url = reverse("group-detail-remove", kwargs={"pk": group_id})
        else:
            url = reverse("group-detail", kwargs={"pk": group_id})
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

    def _vote(self, user_token, group_id=1, show_id=1, vote_type="yes", assert_success=True):
        url = reverse("group-vote-show", kwargs={"group_pk": group_id, "show_pk": show_id})
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user_token)
        request_data = {"vote": vote_type}
        response = self.client.post(url, request_data, format="json")
        content = json.loads(response.content)
        if assert_success:
            self.assertEqual(response.status_code, 200)
            return content["data"]
        self.assertEqual(response.status_code, 404)
        return content["error"]

    def _view_results(self, user_token, group_id=1):
        url = reverse("group-show-list", kwargs={"pk": group_id})
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user_token)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        return data

    def _view_pending(self, user_token, group_id=1):
        url = reverse("group-pending-list", kwargs={"pk": group_id})
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user_token)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        return data

    def _clear(self, user_token, group_id=1):
        url = reverse("group-clear-shows", kwargs={"pk": group_id})
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user_token)
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        return data

    def test_groups(self):
        # group was first created at setup
        self._view_groups(num_groups=1)
        new_group_name = "new dummy name"
        data = self._update_group(name=new_group_name)
        self.assertEqual(data.get("name"), new_group_name)

        new_member_id = 4
        new_show_id = self._create_show().id
        data = self._update_group(name=self.GROUP_NAME, members=[new_member_id], shows=[new_show_id], is_add=True)
        # add to group does not modify group name
        self.assertEqual(data.get("name"), new_group_name)
        self.assertEqual(len(data.get("members")), 4)
        self.assertEqual(len(data.get("shows")), 1)

        data = self._update_group(members=[new_member_id], shows=[new_show_id], is_remove=True)
        # remove from group does not modify group name
        self.assertEqual(data.get("name"), new_group_name)
        self.assertEqual(len(data.get("members")), 3)
        self.assertEqual(len(data.get("shows")), 0)

    def test_vote_pending_and_clear(self):
        new_show_id = self._create_show().id
        new_show_id2 = self._create_show().id
        data = self._update_group(name=self.GROUP_NAME, shows=[new_show_id, new_show_id2], is_add=True)
        self.assertEqual(len(data.get("shows")), 2)

        # haven't voted yet, should have 2 pending shows
        data = self._view_pending(self.user_token)
        self.assertEqual(len(data.get("shows")), 2)

        # only one vote so far
        data = self._vote(user_token=self.user_token, show_id=new_show_id, vote_type="yes")
        self.assertEqual(len(data), 1)

        # view results
        data = self._view_results(self.user_token)
        self.assertEqual(data.get("num_members"), 3)
        self.assertEqual(data.get("num_voted"), 1)
        self.assertTrue(data.get("user_voted"))
        self.assertEqual(len(data.get("results")), 2)
        self.assertEqual(data.get("results")[0]["num_yes_votes"], 1)
        self.assertEqual(data.get("results")[0]["num_maybe_votes"], 0)
        self.assertEqual(data.get("results")[0]["num_no_votes"], 0)

        # other members should have `user_voted` as False
        data = self._view_results(self.user2_token)
        self.assertEqual(data.get("num_members"), 3)
        self.assertEqual(data.get("num_voted"), 1)
        self.assertFalse(data.get("user_voted"))
        self.assertEqual(len(data.get("results")), 2)
        self.assertEqual(data.get("results")[0]["num_yes_votes"], 1)
        self.assertEqual(data.get("results")[0]["num_maybe_votes"], 0)
        self.assertEqual(data.get("results")[0]["num_no_votes"], 0)

        # can't vote more than once with the same vote_type
        error = self._vote(
            user_token=self.user_token, group_id=1, show_id=new_show_id, vote_type="yes", assert_success=False
        )
        self.assertEqual(error, "Already voted yes!")

        # changing vote to "maybe" doesn't result in duplicate votes
        data = self._vote(user_token=self.user_token, group_id=1, show_id=new_show_id, vote_type="maybe")
        self.assertEqual(len(data), 1)

        # pending one more show
        data = self._view_pending(self.user_token)
        self.assertEqual(len(data.get("shows")), 1)

        # viewing group should still have two shows
        data = self._view_group_detail(self.user_token)
        self.assertEqual(len(data.get("shows")), 2)

        # any member can clear shows
        data = self._clear(self.user2_token)
        self.assertEqual(len(data.get("shows")), 0)
