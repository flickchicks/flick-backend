import json

from api import settings as api_settings
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, status, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .models import Comment, Item, Like
from .serializers import ItemDetailSerializer, ItemSerializer


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


class LikeItem(generics.CreateAPIView):
    def post(self, request):
        data = json.loads(request.body)

        if "item_id" not in data:
            return Response({"error": "no item_id in request."}, status=status.HTTP_400_BAD_REQUEST)
        item = Item.objects.get(pk=data["item_id"])

        try:
            print("try")
            like = Like()
            like.item = item
            like.owner = request.user
            like.save()
        except IntegrityError:
            print("catch")
            return Response({"error": "item already liked by this user!"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ItemDetailSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentItem(generics.CreateAPIView):
    def post(self, request):
        data = json.loads(request.body)

        if "item_id" not in data:
            return Response({"error": "no item_id in request."}, status=status.HTTP_400_BAD_REQUEST)

        if "body" not in data:
            return Response({"error": "no body in request."}, status=status.HTTP_400_BAD_REQUEST)
        item = Item.objects.get(pk=data["item_id"])

        comment = Comment()
        comment.item = item
        comment.body = data["body"]
        comment.owner = request.user
        comment.save()

        serializer = ItemDetailSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
