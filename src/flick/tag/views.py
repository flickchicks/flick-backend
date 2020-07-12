from api import settings as api_settings
from api.utils import success_response
from rest_framework import generics

from .models import Tag
from .serializers import TagSerializer


class TagList(generics.ListCreateAPIView):
    """
    Tag: Create, List
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    # if api_settings.UNPROTECTED, then any user can see this
    permission_classes = api_settings.UNPROTECTED

    # don't need this, generics has this code, but this overrides
    # gives option to add additional checks / customize
    def list(self, request):
        # can access logged in user via request.user
        self.serializer_class = TagSerializer
        return super(TagList, self).list(request)

    # for read-only fields you need to pass the value when calling save
    # this is so that when an Tag is created, only the
    # currently authenticated user is linked to the Tag and can
    # be shown in the TagSerializer as "owner"
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Location: Read, Write, Delete
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    permission_classes = api_settings.UNPROTECTED

    def retrieve(self, request, pk):
        queryset = self.get_object()
        serializer = TagSerializer(queryset, many=False)
        return success_response(serializer.data)
