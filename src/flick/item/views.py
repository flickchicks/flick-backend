from django.shortcuts import render

# test
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer

# Create your views here.
from rest_framework import viewsets
from rest_framework import status, generics, mixins

from .serializers import ItemSerializer, ItemDetailSerializer

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
    serializer_class = ItemDetailSerializer
    
    def retrieve(self, request, pk):
        queryset = self.get_object()
        serializer = ItemDetailSerializer(queryset, many=False)
        return Response(serializer.data)

