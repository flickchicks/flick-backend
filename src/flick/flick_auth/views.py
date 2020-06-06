from django.shortcuts import render

from django.contrib.auth import get_user_model
from django.conf import settings as dj_settings
from rest_framework import status, viewsets
from rest_framework.response import Response
from .utils import AuthTools
from api import settings as api_settings
from user.serializers import UserSerializer, ProfileSerializer
from user.models import Profile
from .serializers import LoginSerializer, UserRegisterSerializer, LoginCompleteSerializer, LogoutSerializer
from api.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
import re  # regex engine

User = get_user_model()


class UserView(RetrieveUpdateAPIView):

    model = User
    serializer_class = UserSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get_object(self, *args, **kwargs):
        return self.request.user


class ProfileView(RetrieveUpdateAPIView):

    model = User.profile
    serializer_class = ProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get_object(self, *args, **kwargs):
        return self.request.user.profile


class LoginView(GenericAPIView):

    permission_classes = api_settings.UNPROTECTED
    serializer_class = LoginSerializer

    def get(self, request):
        if request.user.is_anonymous:
            return Response("You are currently not logged in!", status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if "username" in request.data and "social_id_token" in request.data:
            username = request.data["username"]
            social_id_token = request.data["social_id_token"]

            user = AuthTools.authenticate_social_id_token(username, social_id_token)

            if user is not None:  # and AuthTools.login(request, user):
                token = AuthTools.issue_user_token(user, "login")
                serializer = LoginCompleteSerializer(token)
                return Response(serializer.data)

        message = {"error": "Unable to login with the credentials provided."}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS
    serializer_class = LogoutSerializer

    def post(self, request):
        if AuthTools.logout(request):
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class RegisterView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = api_settings.UNPROTECTED

    def perform_create(self, serializer):
        serializer.save()


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = api_settings.UNPROTECTED
