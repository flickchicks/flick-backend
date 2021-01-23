from user.models import Profile

from api.utils import failure_response
from api.utils import success_response
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core import signing
from flick_auth import settings as auth_settings
from lst.models import Lst
import requests
from rest_framework.authtoken.models import Token

from .apple_oauth import AppleAuthController


class AuthenticateController:
    PASSWORD_SALT = auth_settings.AUTH_PASSWORD_SALT
    TOKEN_AGE = auth_settings.AUTH_TOKEN_AGE

    def __init__(self, request, data, serializer):
        self._request = request
        self._data = data
        self._serializer = serializer
        self._name = data.get("name")
        self._username = data.get("username").lower() if data.get("username") else None
        self._email = data.get("email")
        self._profile_pic = self._data.get("profile_pic")
        self._social_id = self._data.get("social_id")
        self._social_id_token = self._data.get("social_id_token")
        self._social_id_token_type = self._data.get("social_id_token_type")

    def _issue_auth_token(self, user, salt):
        if not user:
            return failure_response("Can only issue token to existing users.")
        if salt == "login":
            token, _ = Token.objects.get_or_create(user=user)
        else:
            token = signing.dumps({"id": user.id}, salt=salt)
        return token.key

    def _get_user_from_token(self, token, salt):
        try:
            value = signing.loads(token, salt=self.PASSWORD_SALT, max_age=900)
        except signing.SignatureExpired:
            return None
        except signing.BadSignature:
            return None
        user_exists = User.objects.filter(id=value.get("id"))
        if user_exists:
            return User.objects.get(id=value.get("id"))
        return None

    def _generate_username(self):
        username = self._name.replace(" ", "").lower()
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
        Lst.objects.create(owner=profile, is_saved=True, name="Saved")
        Lst.objects.create(owner=profile, is_watch_later=True, name="Watch Later")
        profile.save()
        return profile

    def _check_facebook_token(self, social_id, social_id_token):
        url = settings.VALIDATE_FACEBOOK_ID_AND_TOKEN_URL + social_id_token
        data = requests.get(url=url).json()
        return not data.get("error") and data.get("id") == social_id

    def _check_apple_token(self, social_id, social_id_token):
        apple_auth_controller = AppleAuthController()
        res = apple_auth_controller.retrieve_token(social_id_token)
        return res is not None

    def _check_token(self, social_id, social_id_token, type):
        if social_id is None or social_id_token is None:
            return False
        if settings.VALIDATE_SOCIAL_TOKEN is False:
            return True
        if type == "apple":
            return self._check_apple_token(social_id, social_id_token)
        if type == "facebook":
            return self._check_facebook_token(social_id, social_id_token)

    def process(self):
        response = self.login()
        if not response:
            return self.register()
        return response

    def login(self):
        user_exists = User.objects.filter(
            profile__social_id=self._social_id, profile__social_id_token_type=self._social_id_token_type, is_active=True
        )
        if not user_exists:
            return None
        user = User.objects.get(
            profile__social_id=self._social_id, profile__social_id_token_type=self._social_id_token_type, is_active=True
        )
        user_exists_with_social_id_token = user.profile.social_id_token == self._social_id_token
        if not user_exists_with_social_id_token:
            # token might have expired, let's see if the social_id_token is correct
            # if so, we update their "password"
            if self._check_token(self._social_id, self._social_id_token, self._social_id_token_type):
                user.set_password(self._social_id_token)
            else:
                return failure_response(
                    f"social_id_token of {self._social_id_token} is invalid or does not match with social_id of {self._social_id}."
                )
        login(self._request, user)
        auth_token = self._issue_auth_token(user, "login")
        return success_response(self._serializer(user, context={"auth_token": auth_token}).data)

    def register(self):
        if not self._check_token(self._social_id, self._social_id_token, self._social_id_token_type):
            return failure_response(
                f"social_id_token of {self._social_id_token} is invalid or does not match with social_id of {self._social_id}."
            )
        if Profile.objects.filter(social_id_token=self._social_id_token):
            return failure_response(f"Profile already exists with the social_id_token {self._social_id_token}.")
        if not self._username:
            if not self._name:
                return failure_response("Must supply a name to get a generated username.")
            self._username = self._generate_username()
        else:
            if User.objects.filter(username=self._username):
                return failure_response(f"Profile already exists with the username {self._username}.")
        user_data = {"username": self._username, "password": self._social_id_token, "email": self._email}
        # can't set this directly in user_data because self._name could be None
        if self._name:
            user_data["first_name"] = self._name
        user = self._create_user(user_data)
        profile_data = {
            "user": user,
            "profile_pic": self._profile_pic,
            "social_id": self._social_id,
            "social_id_token": self._social_id_token,
            "social_id_token_type": self._social_id_token_type,
        }
        self._create_profile(profile_data)
        login(self._request, user)
        auth_token = self._issue_auth_token(user, "login")
        return success_response(self._serializer(user, context={"auth_token": auth_token}).data)
