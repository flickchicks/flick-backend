from django.shortcuts import render

# test
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .models import Item
from .serializers import ItemSerializer

# Create your views here.
from rest_framework import viewsets

from .serializers import UserSerializer
from user.models import User

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer

@csrf_exempt
def item_list(request, *args, **kwargs):
    if request.method == 'GET':
        pk = kwargs.get('pk')
        if pk:
            item = Item.objects.get(pk=pk)
            serializer = ItemSerializer(item, many=False)   
            return JsonResponse(serializer.data, safe=False)
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

