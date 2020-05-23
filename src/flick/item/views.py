from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, mixins

from .models import Item
from .serializers import ItemSerializer

class ItemList(generics.ListCreateAPIView):
    """
    Item: Create, List
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    # don't need this, generics has this code, but this overrides
    # gives option to add additional checks / customize
    def list(self, request):
        self.serializer_class = ItemSerializer
        return super(ItemList, self).list(request)

class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Location: Read, Write, Delete
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    
    def retrieve(self, request, pk):
        queryset = self.get_object()
        serializer = ItemSerializer(queryset, many=False)
        return Response(serializer.data)

