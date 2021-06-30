import json

from api import settings as api_settings
from api.utils import paginated_success_response
from api.utils import success_response
from django.core.paginator import Paginator
from rest_framework import generics

from .models import Tag
from .serializers import TagSerializer


class TagList(generics.GenericAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = api_settings.UNPROTECTED

    def get(self, request):
        try:
            page_number = int(request.query_params.get("page"))
        except Exception:
            page_number = 1
        paginator = Paginator(self.get_queryset(), per_page=4, allow_empty_first_page=True)  # can change later
        tag_page = paginator.get_page(page_number)
        serializer = self.serializer_class(tag_page, many=True)
        return paginated_success_response(
            data=serializer.data,
            next_page_number=tag_page.next_page_number(),
            has_next_page=tag_page.has_next(),
            total_pages=paginator.num_pages,
        )

    def post(self, request):
        data = json.loads(request.body)
        tag_name = data.get("tag")
        if Tag.objects.filter(name__iexact=tag_name):
            return success_response(self.serializer_class(Tag.objects.get(name__iexact=tag_name)).data)
        tag = Tag()
        tag.name = tag_name
        tag.save()
        return success_response(self.serializer_class(tag).data)


class TagDetail(generics.RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = api_settings.UNPROTECTED
