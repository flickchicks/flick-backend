from django.contrib.auth.models import User
from django.conf import settings as dj_settings
from django.shortcuts import render

from rest_framework import generics, status, viewsets
from rest_framework.response import Response

from .utils import AuthTools
from .register_controller import RegisterController
from .serializers import LoginSerializer, UserRegisterSerializer, LoginCompleteSerializer, LogoutSerializer
from api import settings as api_settings
from api.generics import CreateAPIView, RetrieveUpdateAPIView
from api.utils import failure_response, success_response
from user.models import Profile
from user.serializers import UserSerializer, ProfileSerializer

import json
import re


class UserView(generics.GenericAPIView):
    model = Profile
    serializer_class = ProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        profile = Profile.objects.get(user=self.request.user)
        serializer = ProfileSerializer(profile)
        return success_response(serializer.data)

    def post(self, request):
        data = json.loads(request.body)

        profile = Profile.objects.get(user=self.request.user)

        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        profile_pic_base64 = data.get("profile_pic")
        bio = data.get("bio")
        phone_number = data.get("phone_number")
        social_id_token_type = data.get("social_id_token_type")
        social_id_token = data.get("social_id_token")

        if username and self.request.user.username != username:
            self.request.user.username = username
        if first_name and self.request.user.first_name != first_name:
            self.request.user.first_name = first_name
        if last_name and self.request.user.last_name != last_name:
            self.request.user.last_name = last_name
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
            self.request.user.set_password(social_id_token)

        self.request.user.save()
        profile.save()

        serializer = ProfileSerializer(profile)
        return success_response(serializer.data)


class LoginView(generics.GenericAPIView):

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


class LogoutView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS
    serializer_class = LogoutSerializer

    def post(self, request):
        if AuthTools.logout(request):
            return success_response(None)
        return failure_response(None)


class RegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = api_settings.UNPROTECTED

    def post(self, request):
        data = json.loads(request.body)
        return RegisterController(request, data, self.serializer_class).process()


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = api_settings.UNPROTECTED
