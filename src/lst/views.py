import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.db.models import Q
from rest_framework import generics

from .controllers.create_lst_controller import CreateLstController
from .controllers.delete_lst_controller import DeleteLstController
from .controllers.update_lst_controller import UpdateLstController
from .models import Lst
from .serializers import LstWithSimpleShowsSerializer


class LstList(generics.GenericAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstWithSimpleShowsSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        """See all possible lists."""
        if not Profile.objects.filter(user=request.user):
            return failure_response(f"No user to be found with id of {request.user.id}.")
        profile = Profile.objects.get(user=request.user)
        lsts = Lst.objects.filter(Q(owner=profile) | Q(collaborators=profile) | Q(is_private=False))
        serializer = self.serializer_class(lsts, many=True, context={"request": request})
        return success_response(serializer.data)

    def post(self, request):
        """Create a list."""
        data = json.loads(request.body)
        return CreateLstController(request, data, self.serializer_class).process()


class LstDetail(generics.GenericAPIView):
    queryset = Lst.objects.all()
    serializer_class = LstWithSimpleShowsSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        """
        Get a specific list by id.
        If the request user is a collaborator or an owner or is looking at a list that is public,
        then the list will be returned.
        """
        if not Lst.objects.filter(pk=pk):
            return failure_response(f"List of id {pk} does not exist.")
        lst = Lst.objects.get(pk=pk)
        profile = Profile.objects.get(user=request.user)
        if not profile:
            return failure_response(f"No user to be found with id of {request.user.id}.")
        user_is_collaborator = profile in lst.collaborators.all()
        user_is_owner = profile == lst.owner
        if not lst.is_private or user_is_collaborator or user_is_owner:
            serializer = self.serializer_class(lst, many=False, context={"request": request})
            return success_response(serializer.data)
        else:
            return failure_response(
                f"User of id {request.user.id} does not have the right permissions to view list of id {pk}."
            )

    def delete(self, request, pk):
        """
        Delete a list by id.
        Only owners of lists can delete their lists.
        """
        return DeleteLstController(request, pk).process()

    def post(self, request, pk):
        """
        Update a list by id.
        Collaborators can update pic, is_saved, is_watch_later, collaborators, and shows.
        An owner can update name, pic, is_saved, is_private, is_watch_later, collaborators, the owner (can cede ownership completely to another user), and shows.
        """
        data = json.loads(request.body)
        return UpdateLstController(request, pk, data, self.serializer_class).process()


class LstDetailAdd(generics.GenericAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstWithSimpleShowsSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        """
        Update a list by id by adding all of the fields passed in.
        Collaborators can update pic, is_saved, is_watch_later, collaborators, and shows.
        An owner can update name, pic, is_saved, is_private, is_watch_later, collaborators, the owner (can cede ownership completely to another user), and shows.
        """
        data = json.loads(request.body)
        return UpdateLstController(
            request=request, pk=pk, data=data, serializer=self.serializer_class, is_add=True, is_remove=False
        ).process()


class LstDetailRemove(generics.GenericAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstWithSimpleShowsSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        """
        Update a list by id by adding all of the fields passed in.
        Collaborators can update pic, is_saved, is_watch_later, collaborators, and shows.
        An owner can update name, pic, is_saved, is_private, is_watch_later, collaborators, the owner (can cede ownership completely to another user), and shows.
        """
        data = json.loads(request.body)
        return UpdateLstController(
            request=request, pk=pk, data=data, serializer=self.serializer_class, is_add=False, is_remove=True
        ).process()
