from django.contrib.auth import get_user_model
from django.conf import settings as dj_settings
from django.shortcuts import render

from rest_framework import status, viewsets
from rest_framework.response import Response

from .utils import AuthTools
from .serializers import LoginSerializer, UserRegisterSerializer, LoginCompleteSerializer, LogoutSerializer
from api import settings as api_settings
from api.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from api.utils import failure_response, success_response
from user.models import Profile
from user.serializers import UserSerializer, ProfileSerializer

import re

User = get_user_model()


class UserView(GenericAPIView):
    model = Profile
    serializer_class = ProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        profile = Profile.objects.get(user=self.request.user)
        serializer = ProfileSerializer(profile)
        return success_response(serializer.data)


class ProfileView(RetrieveUpdateAPIView):

    model = Profile
    serializer_class = ProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get_object(self, *args, **kwargs):
        return success_response(self.request.profile)


class LoginView(GenericAPIView):

    permission_classes = api_settings.UNPROTECTED
    serializer_class = LoginSerializer

    def get(self, request):
        if request.user.is_anonymous:
            return success_response("You are currently not logged in!")
        serializer = UserSerializer(request.user)
        return success_response(serializer.data)

    def post(self, request):
        if "username" in request.data and "social_id_token" in request.data:
            username = request.data["username"]
            social_id_token = request.data["social_id_token"]

            user = AuthTools.authenticate_social_id_token(username, social_id_token)

            if user is not None:  # and AuthTools.login(request, user):
                token = AuthTools.issue_user_token(user, "login")
                serializer = LoginCompleteSerializer(token)
                return success_response(serializer.data)

        message = {"Unable to login with the credentials provided."}
        return failure_response(message)


class LogoutView(GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS
    serializer_class = LogoutSerializer

    def post(self, request):
        if AuthTools.logout(request):
            return success_response(None)

        return failure_response(None)


class RegisterView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = api_settings.UNPROTECTED

    def perform_create(self, serializer):
        serializer.save()


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = api_settings.UNPROTECTED
