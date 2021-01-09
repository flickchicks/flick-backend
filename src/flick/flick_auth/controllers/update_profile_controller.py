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
        name = self._data.get("name")
        profile_pic_base64 = self._data.get("profile_pic")
        email = self._data.get("email", "")
        bio = self._data.get("bio")
        phone_number = self._data.get("phone_number")
        social_id = self._data.get("social_id")
        social_id_token = self._data.get("social_id_token")
        social_id_token_type = self._data.get("social_id_token_type")

        if username is not None and self._user.username != username:
            if len(username) > 30 or len(username) < 3:
                return failure_response("Username must be between 3 and 30 characters.")
            if User.objects.filter(username__iexact=username):
                return failure_response("Username is already taken.")
            self._user.username = username
        if name is not None and self._user.first_name != name:
            self._user.first_name = name
        if email is not None and self._user.email != email:
            self._user.email = email
        if profile_pic_base64 is not None:
            if profile_pic_base64 == "":
                profile.remove_profile_pic()
            else:
                profile.profile_pic = profile_pic_base64
        if bio is not None and profile.bio != bio:
            profile.bio = bio
        if phone_number is not None and profile.phone_number != phone_number:
            profile.phone_number = phone_number
        if social_id is not None and profile.social_id != social_id:
            profile.social_id = social_id
        if social_id_token_type is not None and profile.social_id_token_type != social_id_token_type:
            profile.social_id_token_type = social_id_token_type
        if social_id_token is not None and profile.social_id_token != social_id_token:
            profile.social_id_token = social_id_token
            self._user.set_password(social_id_token)

        self._user.save()
        profile.save()
        return success_response(self._serializer(profile).data)
