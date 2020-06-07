from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from friend.serializers import FriendUserSerializer
from friendship.models import Friend, Follow, Block

from rest_framework import generics, mixins, status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, CurrentUserDefault

from api import settings as api_settings


class FriendList(APIView):
    """
    List all friends.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, format=None):
        friends = [User.objects.get(pk=friend.pk) for friend in Friend.objects.friends(user=request.user)]
        serializer = FriendUserSerializer(friends, many=True)
        return Response(serializer.data)
