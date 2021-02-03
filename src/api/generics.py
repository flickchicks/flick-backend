from api import settings
from rest_framework import generics
from rest_framework import mixins


class GenericAPIView(generics.GenericAPIView):
    """
    Base class for all generic views
    """

    permission_classes = settings.STANDARD_PERMISSIONS
    is_user = False

    def get_queryset(self):
        queryset = super(generics.GenericView, self).get_queryset()

        user = self.request.user
        # profile = None
        # if not user.is_anonymous():
        #     profile = user.profile

        if not user.is_superuser:
            if self.is_user:
                queryset = queryset.filter(id=user.id)
        return queryset


class CreateAPIView(mixins.CreateModelMixin, GenericAPIView):
    """
    Concrete view for creating a model instance
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()


class ListAPIView(mixins.ListModelMixin, GenericAPIView):
    """
    Concrete view for listing a queryset
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin, GenericAPIView):
    """
    Concrete view for retrieving a model instance
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()


class RetrieveUpdateAPIView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericAPIView):
    """
    Concrete view for retrieving, updating, or deleting a model instance
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView
):
    """
    Concrete view for retrieving, updating, or deleting a model instance
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
