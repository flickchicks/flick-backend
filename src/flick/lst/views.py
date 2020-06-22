from django.contrib.auth import get_user_model
from django.conf import settings as dj_settings
from django.shortcuts import render

from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Lst
from .serializers import LstSerializer
from api import settings as api_settings
from api.generics import GenericAPIView
from api.utils import failure_response, success_response
from user.models import Profile

import json
import re


class LstView(GenericAPIView):
    model = Lst
    serializer_class = LstSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        profile = Profile.objects.get(user=self.request.user)
        print("owner_lsts: ", profile.owner_lsts)
        serializer = LstSerializer(profile.owner_lsts)
        return success_response(serializer.data)

    def post(self, request):
        return success_response("lstview post")
