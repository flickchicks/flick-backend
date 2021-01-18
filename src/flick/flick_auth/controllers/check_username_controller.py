from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User


class CheckUsernameController:
    def __init__(self, request, data):
        self._request = request
        self._data = data

    def process(self):
        username = self._data.get("username").lower() if self._data.get("username") else ""
        if len(username) > 30:
            return failure_response("Username must be 30 characters or less.")
        if len(username) < 3:
            return failure_response("Username must be at least three characters.")
        if User.objects.filter(username__iexact=username):
            return failure_response("Username is already taken.")
        return success_response("Username is available!")
