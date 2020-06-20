from api import settings as api_settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.serializers import CurrentUserDefault, ModelSerializer, PrimaryKeyRelatedField
from rest_framework.views import APIView

from friend.serializers import FriendUserSerializer, FriendRequestSerializer, FriendshipSerializer
from friendship.models import Follow, Friend, FriendshipRequest, Block

from api.utils import failure_response, success_response
import json


class FriendList(APIView):
    """
    List all friends.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, format=None):
        friends = [User.objects.get(pk=friend.pk) for friend in Friend.objects.friends(user=request.user)]
        serializer = FriendUserSerializer(friends, many=True)
        return success_response(serializer.data)


class FriendRequestListAndCreate(generics.ListCreateAPIView):
    """
    List and create friend requests.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, format=None):
        friend_requests = Friend.objects.sent_requests(user=request.user)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return success_response(serializer.data)

    def post(self, request, format=None):
        data = json.loads(request.body)
        friend_requests = []
        for username in data.get("usernames"):
            try:
                user = User.objects.get(username=username)
                friend_requests.append(Friend.objects.add_friend(request.user, user))
            except Exception as e:
                # return failure_response(str(e))
                print(str(e))  # what to do with the messages from requests that failed?
                continue

        serializer = FriendRequestSerializer(friend_requests, many=True)
        return success_response(serializer.data)


class FriendAcceptListAndCreate(generics.ListCreateAPIView):
    """
    List and create friend requests.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, format=None):
        friend_requests = Friend.objects.unrejected_requests(user=request.user)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return success_response(serializer.data)

    def post(self, request, format=None):
        data = json.loads(request.body)
        friends_accepted = []
        for username in data.get("usernames"):
            friend = User.objects.get(username=username)
            user_pk = request.user.pk
            friend_request = FriendshipRequest.objects.get(from_user=friend.pk, to_user=user_pk)
            friend_request.accept()
            friends_accepted.append(friend_request)

        serializer = FriendshipSerializer(friends_accepted, many=True)

        return success_response(serializer.data)


class FriendRejectListAndCreate(generics.ListCreateAPIView):
    """
    List and create friend requests.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, format=None):
        friend_requests = Friend.objects.rejected_requests(user=request.user)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return success_response(serializer.data)

    def post(self, request, format=None):
        data = json.loads(request.body)
        friends_rejected = []
        for username in data.get("usernames"):
            friend = User.objects.get(username=username)
            user_pk = request.user.pk
            friend_request = FriendshipRequest.objects.get(from_user=friend.pk, to_user=user_pk)
            friend_request.reject()
            friends_rejected.append(friend_request)

        serializer = FriendRequestSerializer(friends_rejected, many=True)

        return success_response(serializer.data)


class FriendRemoveListAndCreate(generics.ListCreateAPIView):
    """
    List and create friend requests.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, format=None):
        data = json.loads(request.body)
        friends_removed = []
        for username in data.get("usernames"):
            try:
                friend = User.objects.get(username=username)
                Friend.objects.remove_friend(request.user, friend)
                friends_removed.append(friend)
            except Exception as e:
                print(e)
                continue

        serializer = FriendUserSerializer(friends_removed, many=True)

        return success_response(serializer.data)
