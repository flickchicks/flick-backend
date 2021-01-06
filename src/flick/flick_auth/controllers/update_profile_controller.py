from user.models import Profile

from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User


class UpdateProfileController:
    def __init__(self, request, data, serializer):
        self._request = request
        self._user = self._request.user
        self._data = data
        self._serializer = serializer

    def process(self):
        profile_exists = Profile.objects.filter(user=self._user)
        if not profile_exists:
            return failure_response(f"Profile for user {self._user} does not exist!")
        profile = Profile.objects.get(user=self._user)

        username = self._data.get("username")
        first_name = self._data.get("first_name")
        last_name = self._data.get("last_name")
        profile_pic_base64 = self._data.get("profile_pic")
        email = self._data.get("email", "")
        bio = self._data.get("bio")
        phone_number = self._data.get("phone_number")
        social_id_token = self._data.get("social_id_token")
        social_id_token_type = self._data.get("social_id_token_type")

        if username and self._user.username != username:
            if len(username) > 30 or len(username) < 3:
                return failure_response("Username must be between 3 and 30 characters.")
            if User.objects.filter(username__iexact=username):
                return failure_response("Username is already taken.")
            self._user.username = username
        if first_name and self._user.first_name != first_name:
            self._user.first_name = first_name
        if last_name and self._user.last_name != last_name:
            self._user.last_name = last_name
        if email and self._user.email != email:
            self._user.email = email
        if profile_pic_base64:
            profile.profile_pic = profile_pic_base64
        if bio and profile.bio != bio:
            profile.bio = bio
        if phone_number and profile.phone_number != phone_number:
            profile.phone_number = phone_number
        if social_id_token_type and profile.social_id_token_type != social_id_token_type:
            profile.social_id_token_type = social_id_token_type
        if social_id_token and profile.social_id_token != social_id_token:
            profile.social_id_token = social_id_token
            self._user.set_password(social_id_token)

        self._user.save()
        profile.save()
        return success_response(self._serializer(profile).data)
