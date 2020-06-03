import json

from api import settings as api_settings
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .models import Show
from .serializers import ShowSerializer


class ShowViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Show: see all shows, get a specific show
    """

    queryset = Show.objects.all()
    serializer_class = ShowSerializer

    # if api_settings.UNPROTECTED, then any user can see this
    permission_classes = api_settings.STANDARD_PERMISSIONS

    # don't need this, generics has this code, but this overrides
    # gives option to add additional checks / customize
    # def list(self, request):
    #     # can access logged in user via request.user
    #     self.serializer_class = ShowSerializer
    #     return super(ItemList, self).list(request)

    # def retrieve(self, request, pk):
    #     queryset = self.get_object()
    #     serializer = ShowDetailSerializer(queryset, many=False)
    #     return Response(serializer.data)
