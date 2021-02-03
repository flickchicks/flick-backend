import json
from user.models import Profile
from user.serializers import ProfileSerializer
from user.serializers import UserProfileSerializer

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from rest_framework import generics
from rest_framework.authtoken.models import Token

from .controllers.authenticate_controller import AuthenticateController
from .controllers.check_username_controller import CheckUsernameController
from .controllers.update_profile_controller import UpdateProfileController
from .serializers import AuthenticateSerializer
from .serializers import LogoutSerializer


class UserView(generics.GenericAPIView):
    model = Profile
    serializer_class = ProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        profile = Profile.objects.get(user=self.request.user)
        serializer = self.serializer_class(profile)
        return success_response(serializer.data)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.data
        return UpdateProfileController(request, data, self.serializer_class).process()


class CheckUsernameView(generics.GenericAPIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.data
        return CheckUsernameController(request, data).process()


class UserProfileView(generics.GenericAPIView):
    model = Profile
    serializer_class = UserProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        if request.user.id == pk:
            return HttpResponseRedirect(reverse("me"))
        if not User.objects.filter(id=pk):
            return failure_response(f"User of id {pk} not found.")
        profile = Profile.objects.get(user__id=pk)
        return success_response(self.serializer_class(profile, context={"request": self.request}).data)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def logout(self, request):
        if request:
            try:
                Token.objects.filter(user=request.user).delete()
                logout(request)
                return True
            except Exception as e:
                print(e)
                pass
        return False

    def post(self, request):
        if self.logout(request):
            return success_response(None)
        return failure_response(None)


class AuthenticateView(generics.GenericAPIView):
    serializer_class = AuthenticateSerializer
    permission_classes = api_settings.UNPROTECTED

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.data
        return AuthenticateController(request, data, self.serializer_class).process()
