from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core import signing
from flick_auth import settings as auth_settings
from rest_framework.authtoken.models import Token


class LoginController:
    PASSWORD_SALT = auth_settings.AUTH_PASSWORD_SALT
    TOKEN_AGE = auth_settings.AUTH_TOKEN_AGE

    def __init__(self, request, data, serializer):
        self._request = request
        self._data = data
        self._serializer = serializer

    def _authenticate(self, username, social_id_token):
        user_exists = User.objects.filter(username=username, is_active=True)
        if user_exists:
            return authenticate(username=username, password=social_id_token)
        return None

    def _login(self, user):
        if user:
            login(self._request, user)
            return True
        return False

    def _issue_auth_token(self, user, salt):
        if not user:
            return failure_response("Can only issue token to existing users.")
        if salt == "login":
            token, _ = Token.objects.get_or_create(user=user)
        else:
            token = signing.dumps({"id": user.id}, salt=salt)
        return token

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

    def process(self):
        username = self._data.get("username")
        social_id_token = self._data.get("social_id_token")
        user = self._authenticate(username, social_id_token)
        if not user:
            return failure_response(f"User with username {username} could be authenticated.")
        if self._login(user):
            token = self._issue_auth_token(user, "login")
            return success_response(self._serializer(token).data)
        return failure_response("Could not generate auth token for credentials provided.")
