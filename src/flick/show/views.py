from api import settings as api_settings
from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.views import APIView

from .models import Show
from .serializers import ShowSerializer


class ShowViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Show: see all shows, get a specific show
    """

    queryset = Show.objects.all()
    serializer_class = ShowSerializer

    permission_classes = api_settings.STANDARD_PERMISSIONS
