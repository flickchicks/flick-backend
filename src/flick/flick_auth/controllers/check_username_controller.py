from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User


class CheckUsernameController:
    def __init__(self, request, data):
        self._request = request
        self._data = data

    def process(self):
        username = self._data.get("username")
        if len(username) > 30:
            return failure_response(f"{username} must be 30 characters or less.")
        if User.objects.filter(username=username):
            return failure_response(f"{username} is already taken.")
        return success_response(f"{username} is available!")
