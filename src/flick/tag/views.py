import json

from api import settings as api_settings
from api.utils import success_response
from rest_framework import generics

from .models import Tag
from .serializers import TagSerializer


class TagList(generics.GenericAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = api_settings.UNPROTECTED

    def get(self, request):
        return success_response(self.serializer_class(self.get_queryset(), many=True).data)

    def post(self, request):
        data = json.loads(request.body)
        tag_name = data.get("tag")
        if Tag.objects.filter(tag__iexact=tag_name):
            return success_response(self.serializer_class(Tag.objects.get(tag__iexact=tag_name)).data)
        tag = Tag()
        tag.name = tag_name
        tag.save()
        return success_response(self.serializer_class(tag).data)


class TagDetail(generics.RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = api_settings.UNPROTECTED
