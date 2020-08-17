import json
from user.models import Profile
from user.serializers import ProfileSerializer
from user.serializers import UserSerializer

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from rest_framework import generics

from .controllers.login_controller import LoginController
from .controllers.register_controller import RegisterController
from .controllers.update_profile_controller import UpdateProfileController
from .serializers import LoginSerializer
from .serializers import LogoutSerializer
from .serializers import RegisterSerializer
from .utils import AuthTools


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


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = api_settings.UNPROTECTED

    def get(self, request):
        if request.user.is_anonymous:
            return success_response("You are currently not logged in!")
        serializer = UserSerializer(request.user)
        return success_response(serializer.data)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.data
        return LoginController(request, data, self.serializer_class).process()


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request):
        if AuthTools.logout(request):
            return success_response(None)
        return failure_response(None)


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = api_settings.UNPROTECTED

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.data
        return RegisterController(request, data, self.serializer_class).process()
