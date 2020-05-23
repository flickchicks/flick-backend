from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, mixins

from .serializers import AssetBundleSerializer, AssetBundleDetailSerializer
from .models import AssetBundle

class AssetBundleList(generics.ListCreateAPIView):
    """
    Item: Create, List
    """
    queryset = AssetBundle.objects.all()
    serializer_class = AssetBundleSerializer

    # don't need this, generics has this code, but this overrides
    # gives option to add additional checks / customize
    def list(self, request):
        self.serializer_class = AssetBundleSerializer
        return super(AssetBundleList, self).list(request)

class AssetBundleDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Location: Read, Write, Delete
    """
    queryset = AssetBundle.objects.all()
    serializer_class = AssetBundleDetailSerializer
    
    def retrieve(self, request, pk):
        queryset = self.get_object()
        serializer = AssetBundleDetailSerializer(queryset, many=False)
        return Response(serializer.data)

