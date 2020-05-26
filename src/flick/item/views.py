from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, mixins

from .models import Item
from .serializers import ItemSerializer, ItemDetailSerializer
from api import settings as api_settings

class ItemList(generics.ListCreateAPIView):
    """
    Item: Create, List
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    # if api_settings.UNPROTECTED, then any user can see this
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    # don't need this, generics has this code, but this overrides
    # gives option to add additional checks / customize
    def list(self, request):
        # can access logged in user via request.user
        self.serializer_class = ItemSerializer
        return super(ItemList, self).list(request)
    
    # for read-only fields you need to pass the value when calling save
    # this is so that when an item is created, only the 
    # currently authenticated user is linked to the item and can
    # be shown in the ItemSerializer as "owner"
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Location: Read, Write, Delete
    """
    queryset = Item.objects.all()
    serializer_class = ItemDetailSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS
    
    def retrieve(self, request, pk):
        queryset = self.get_object()
        serializer = ItemDetailSerializer(queryset, many=False)
        return Response(serializer.data)

