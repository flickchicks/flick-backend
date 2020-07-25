from user.models import Profile

from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from lst.models import Lst


class RegisterController:
    def __init__(self, request, data, serializer):
        self._request = request
        self._data = data
        self._serializer = serializer

    def _generate_username(self, first_name, last_name):
        username = first_name + last_name
        user_exists = User.objects.filter(username=username)
        if not user_exists:
            return username
        count = "1"
        while User.objects.filter(username=username + count):
            count = str(int(count) + 1)
        return username + count

    def _create_user(self, user_data):
        return User.objects._create_user(**user_data)

    def _create_profile(self, profile_data):
        profile = Profile(**profile_data)
        profile.save()
        if not Group.objects.filter(name="consumer_basic"):
            group = Group()
            group.name = "consumer_basic"
            group.save()
        profile.group = Group.objects.get(name="consumer_basic")
        Lst.objects.create(owner=profile, is_saved=True, lst_name="Saved")
        Lst.objects.create(owner=profile, is_watch_later=True, lst_name="Watch Later")
        profile.save()
        return profile

    def process(self):
        username = self._data.get("username")
        first_name = self._data.get("first_name")
        last_name = self._data.get("last_name")
        profile_pic = self._data.get("profile_pic")
        social_id_token = self._data.get("social_id_token")
        social_id_token_type = self._data.get("social_id_token_type")
        if not username and not social_id_token:
            return failure_response("Neither username nor social_id_token supplied.")
        if not username:
            # verify that social_id_token is unique
            profile_exists = Profile.objects.filter(social_id_token=social_id_token)
            if profile_exists:
                return failure_response("Profile already exists with the social_id_token.")
            # generate username based on first_name and last_name
            if not first_name:
                return failure_response("Must supply a first_name to get a generated username.")
            username = self._generate_username(first_name, last_name)
        else:
            # verify that username is unique
            user_exists = User.objects.filter(username=username)
            if user_exists:
                return failure_response("User already exists with the username.")
            # verify that social_id_token is unique
            profile_exists = Profile.objects.filter(social_id_token=social_id_token)
            if profile_exists:
                return failure_response("Profile already exists with the social_id_token.")
        user_data = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "password": social_id_token,
            "email": "",
        }
        user = self._create_user(user_data)
        profile_data = {
            "user": user,
            "profile_pic": profile_pic,
            "social_id_token": social_id_token,
            "social_id_token_type": social_id_token_type,
        }
        self._create_profile(profile_data)
        return success_response(self._serializer(user).data)
