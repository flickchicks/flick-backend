import json
import random
import string

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from friendship.models import Friend
from rest_framework.test import APIClient
from show.models import Show
from tag.models import Tag


class UpdateLstTests(TestCase):
    REGISTER_URL = reverse("register")
    LOGIN_URL = reverse("login")
    CREATE_LST_URL = reverse("lst-list")
    NOTIFICATIONS_URL = reverse("notif-list")
    LST_ID = 7  # each user has 2 default lists, and we intend to create 3 test users
    UPDATE_LST_URL = reverse("lst-detail", kwargs={"pk": LST_ID})
    ADD_TO_LST_URL = reverse("lst-detail-add", kwargs={"pk": LST_ID})
    REMOVE_FROM_LST_URL = reverse("lst-detail-remove", kwargs={"pk": LST_ID})
    OLD_LST_NAME = "Alanna's Kdramas"

    def setUp(self):
        self.client = APIClient()
        self.user_token = self._create_user_and_login()
        self.friend_token = self._create_user_and_login()
        self.friend2_token = self._create_user_and_login()
        self._create_friendship(user1=User.objects.get(id=1), user2=User.objects.get(id=2))
        self._create_friendship(user1=User.objects.get(id=1), user2=User.objects.get(id=3))
        self._create_friendship(user1=User.objects.get(id=2), user2=User.objects.get(id=3))

    def _create_show(self):
        show = Show()
        show.title = self._get_random_string()
        show.ext_api_id = 1
        show.ext_api_source = "tmdb"
        show.poster_pic = self._get_random_string()
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

    def _get_random_string(self):
        return "".join(random.choice(string.digits) for i in range(5))

    def _get_created_show_ids(self, num_shows):
        return [self._create_show().id for n in range(num_shows)]

    def _get_created_tag_ids(self, num_tags):
        return [Tag.objects.create(name=self._get_random_string()).id for n in range(num_tags)]

    def _create_user_and_login(self):
        """Returns the auth token."""
        random_string = self._get_random_string()
        register_data = {
            "username": "",
            "first_name": "Alanna",
            "last_name": "Zhou",
            "profile_pic": "",
            "social_id_token": random_string,
            "social_id_token_type": "test",
        }
        response = self.client.post(self.REGISTER_URL, register_data)
        self.assertEqual(response.status_code, 200)
        username = json.loads(response.content)["data"]["username"]

        login_data = {"username": username, "social_id_token": random_string}
        response = self.client.post(self.LOGIN_URL, login_data)
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.content)["data"]["auth_token"]
        return token

    def _create_friendship(self, user1, user2):
        Friend.objects.add_friend(user1, user2).accept()

    def _create_list(self, collaborators=[], shows=[]):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token)
        request_data = {
            "name": self.OLD_LST_NAME,
            "is_private": False,
            "collaborators": collaborators,
            "shows": shows,
            "tags": [],
        }
        response = self.client.post(self.CREATE_LST_URL, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertEqual(data["is_private"], False)
        self.assertEqual(len(data["collaborators"]), len(collaborators))
        self.assertEqual(len(data["tags"]), 0)
        self.assertEqual(len(data["shows"]), len(shows))
        self.assertEqual(data["owner"]["id"], 1)
        return data

    def _update_list(
        self,
        token=None,
        name="",
        is_private=False,
        collaborators=[],
        shows=[],
        tags=[],
        is_add=False,
        is_remove=False,
        owner=None,
    ):
        token = token or self.user_token
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        request_data = {
            "name": name,
            "is_private": is_private,
            "collaborators": collaborators,
            "shows": shows,
            "tags": tags,
            "owner": owner,
        }
        url = self.UPDATE_LST_URL
        if is_add:
            url = self.ADD_TO_LST_URL
        elif is_remove:
            url = self.REMOVE_FROM_LST_URL
        response = self.client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)["data"]

    def _check_list_edit_notification(self, num_shows_added=None, num_shows_removed=None):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)
        response = self.client.get(self.NOTIFICATIONS_URL)
        data = json.loads(response.content)["data"]
        self.assertEqual(data[1]["notif_type"], "list_invite")
        self.assertEqual(data[1]["from_user"]["id"], 1)
        self.assertEqual(data[1]["to_user"]["id"], 2)
        self.assertEqual(data[1]["lst"]["id"], self.LST_ID)
        self.assertEqual(data[0]["notif_type"], "list_edit")
        self.assertEqual(data[0]["from_user"]["id"], 1)
        self.assertEqual(data[0]["to_user"]["id"], 2)
        self.assertEqual(data[0]["num_shows_added"], num_shows_added)
        self.assertEqual(data[0]["num_shows_removed"], num_shows_removed)

    def test_update_lst(self):
        self._create_list()
        show_ids = self._get_created_show_ids(num_shows=2)
        tag_ids = self._get_created_tag_ids(num_tags=2)
        name = "Updated kdramaz"
        is_private = True
        data = self._update_list(name=name, is_private=is_private, collaborators=[2], shows=show_ids, tags=tag_ids)
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(data["name"], name)
        self.assertEqual(data["is_private"], is_private)
        # regular list update does not allow list-type fields to be modified!
        self.assertEqual(len(data["collaborators"]), 0)
        self.assertEqual(len(data["shows"]), 0)
        self.assertEqual(len(data["tags"]), 0)

    def test_update_lst_no_name(self):
        self._create_list()
        show_ids = self._get_created_show_ids(num_shows=2)
        tag_ids = self._get_created_tag_ids(num_tags=2)
        is_private = True
        data = self._update_list(is_private=is_private, collaborators=[2], shows=show_ids, tags=tag_ids)
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(data["name"], self.OLD_LST_NAME)
        self.assertEqual(data["is_private"], is_private)
        # regular list update does not allow list-type fields to be modified!
        self.assertEqual(len(data["collaborators"]), 0)
        self.assertEqual(len(data["shows"]), 0)
        self.assertEqual(len(data["tags"]), 0)

    def test_transfer_ownership_lst_edit_notification(self):
        self._create_list(collaborators=[2])
        data = self._update_list(owner=2, is_add=True)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.friend_token)
        response = self.client.get(self.NOTIFICATIONS_URL)
        data = json.loads(response.content)["data"][0]
        self.assertEqual(data["notif_type"], "list_edit")
        self.assertEqual(data["from_user"]["id"], 1)
        self.assertEqual(data["to_user"]["id"], 2)
        self.assertEqual(data["lst"]["id"], self.LST_ID)
        self.assertEqual(data["new_owner"]["id"], 2)
        self.assertEqual(data["num_shows_added"], None)
        self.assertEqual(data["num_shows_removed"], None)
        self.assertEqual(data["friend_request_accepted"], None)

    def test_shows_added_to_lst_edit_notification(self):
        self._create_list(collaborators=[2])
        show_ids = self._get_created_show_ids(num_shows=3)
        data = self._update_list(shows=show_ids, is_add=True)
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(len(data["collaborators"]), 1)
        self.assertEqual(len(data["shows"]), len(show_ids))
        self._check_list_edit_notification(num_shows_added=len(show_ids))

    def test_shows_removed_from_lst_edit_notification(self):
        show_ids = self._get_created_show_ids(num_shows=3)
        self._create_list(collaborators=[2], shows=show_ids)
        data = self._update_list(shows=show_ids, is_remove=True)
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(len(data["collaborators"]), 1)
        self.assertEqual(len(data["shows"]), 0)
        self._check_list_edit_notification(num_shows_removed=len(show_ids))

    def _check_collaborators_modified_lst_edit_notification(
        self, from_user_id=1, notified_c_tokens=[], c_ids_added=[], c_ids_removed=[]
    ):
        for token in notified_c_tokens:
            self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
            response = self.client.get(self.NOTIFICATIONS_URL)
            data = json.loads(response.content)["data"][0]
            self.assertEqual(data["notif_type"], "list_edit")
            self.assertEqual(data["from_user"]["id"], from_user_id)
            self.assertEqual(data["lst"]["id"], self.LST_ID)
            self.assertEqual(len(data["collaborators_added"]), len(c_ids_added))
            self.assertEqual(len(data["collaborators_removed"]), len(c_ids_removed))
            for i in range(len(c_ids_added)):
                self.assertEqual(data["collaborators_added"][i]["id"], c_ids_added[i])
            for i in range(len(c_ids_removed)):
                self.assertEqual(data["collaborators_removed"][i]["id"], c_ids_removed[i])

    def test_collaborators_modified_by_owner_lst_edit_notification(self):
        self._create_list(collaborators=[2])
        data = self._update_list(collaborators=[3], is_add=True)
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(len(data["collaborators"]), 2)
        self._check_collaborators_modified_lst_edit_notification(notified_c_tokens=[self.friend_token], c_ids_added=[3])

        data = self._update_list(collaborators=[3], is_remove=True)
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(len(data["collaborators"]), 1)
        self._check_collaborators_modified_lst_edit_notification(
            notified_c_tokens=[self.friend_token, self.friend2_token], c_ids_removed=[3]
        )

    def test_collaborators_modified_by_collaborator_lst_edit_notification(self):
        self._create_list(collaborators=[2])
        data = self._update_list(token=self.friend_token, collaborators=[3], is_add=True)
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(len(data["collaborators"]), 2)
        self._check_collaborators_modified_lst_edit_notification(
            from_user_id=2, notified_c_tokens=[self.user_token], c_ids_added=[3]
        )

        data = self._update_list(token=self.friend_token, collaborators=[3], is_remove=True)
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(len(data["collaborators"]), 1)
        self._check_collaborators_modified_lst_edit_notification(
            from_user_id=2, notified_c_tokens=[self.user_token, self.friend2_token], c_ids_removed=[3]
        )

    def test_add_and_remove_from_lst(self):
        self._create_list()
        show_ids = self._get_created_show_ids(num_shows=2)
        tag_ids = self._get_created_tag_ids(num_tags=2)
        name = "Updated kdramaz"
        is_private = True
        data = self._update_list(
            name=name, is_private=is_private, collaborators=[2], shows=show_ids, tags=tag_ids, is_add=True
        )
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(data["name"], name)
        self.assertEqual(data["is_private"], is_private)
        self.assertEqual(len(data["collaborators"]), 1)
        self.assertEqual(len(data["shows"]), 2)
        self.assertEqual(len(data["tags"]), 2)

        data = self._update_list(
            name=name, is_private=is_private, collaborators=[2], shows=show_ids, tags=tag_ids, is_remove=True
        )
        self.assertEqual(data["id"], self.LST_ID)
        self.assertEqual(data["name"], name)
        self.assertEqual(data["is_private"], is_private)
        self.assertEqual(len(data["collaborators"]), 0)
        self.assertEqual(len(data["shows"]), 0)
        self.assertEqual(len(data["tags"]), 0)
