from django.contrib.auth import get_user_model
from django.conf import settings as dj_settings
from django.shortcuts import render

from rest_framework import generics, mixins, status, viewsets
from rest_framework.response import Response

from .models import Lst
from .serializers import LstSerializer
from api import settings as api_settings
from api.utils import failure_response, success_response
from user.models import Profile

import json
import re


class LstView(generics.GenericAPIView):
    model = Lst
    serializer_class = LstSerializer
    permission_classes = api_settings.UNPROTECTED

    def get(self, request):
        profile = Profile.objects.get(user=self.request.user)
        print("owner_lsts: ", profile.owner_lsts)
        serializer = LstSerializer(profile.owner_lsts)
        return success_response(serializer.data)

    def post(self, request):
        return success_response("lstview post")


class LstList(generics.ListCreateAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstSerializer

    # if api_settings.UNPROTECTED, then any user can see this
    permission_classes = api_settings.UNPROTECTED

    # don't need this, generics has this code, but this overrides
    # gives option to add additional checks / customize
    def list(self, request):
        # can access logged in user via request.user
        self.serializer_class = LstSerializer
        return super(LstList, self).list(request)

    # for read-only fields you need to pass the value when calling save
    # this is so that when an Lst is created, only the
    # currently authenticated user is linked to the Lst and can
    # be shown in the LstSerializer as "owner"
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LstDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstSerializer

    permission_classes = api_settings.UNPROTECTED

    def retrieve(self, request, pk):
        queryset = self.get_object()
        serializer = LstSerializer(queryset, many=False)
        return success_response(serializer.data)
