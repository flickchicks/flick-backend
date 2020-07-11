import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics
from show.models import Show

from .models import Lst
from .serializers import LstSerializer


class LstList(generics.GenericAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        """See all possible lists."""
        if not Profile.objects.filter(user=request.user):
            return failure_response(f"No user to be found with id of {request.user.id}.")
        profile = Profile.objects.get(user=request.user)
        lsts = Lst.objects.filter(Q(owner=profile) | Q(collaborators=profile) | Q(is_private=False))
        serializer = LstSerializer(lsts, many=True)
        return success_response(serializer.data)

    def post(self, request):
        """Create a list."""
        data = json.loads(request.body)
        lst_name = data.get("lst_name")
        lst_pic = data.get("lst_pic")
        is_favorite = data.get("is_favorite", False)
        is_private = data.get("is_private", False)
        is_watched = data.get("is_watched", False)
        collaborator_ids = data.get("collaborators", [])
        show_ids = data.get("shows", [])

        lst = Lst()
        lst.lst_name = lst_name
        lst.lst_pic = lst_pic
        lst.is_favorite = is_favorite
        lst.is_private = is_private
        lst.is_watched = is_watched
        profile = Profile.objects.get(user=request.user)
        lst.owner = profile
        lst.save()

        for c_id in collaborator_ids:
            collaborator = User.objects.get(pk=c_id)
            if Profile.objects.filter(user=collaborator):
                c = Profile.objects.get(user=collaborator)
                lst.collaborators.add(c)
        for show_id in show_ids:
            if Show.objects.filter(pk=show_id):
                show = Show.objects.get(pk=show_id)
                lst.shows.add(show)
        lst.save()
        serializer = LstSerializer(lst)
        return success_response(serializer.data)


class LstDetail(generics.GenericAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstSerializer

    permission_classes = api_settings.UNPROTECTED

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
            serializer = LstSerializer(lst, many=False)
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
        if not Lst.objects.filter(pk=pk):
            return failure_response(f"List of id {pk} does not exist.")
        lst = Lst.objects.get(pk=pk)
        profile = Profile.objects.get(user=request.user)
        if not profile == lst.owner:
            return failure_response(f"User of id {request.user.id} is not the owner of list of id {pk}.")
        lst.delete()
        return success_response(f"List of id {pk} has been deleted.")

    def post(self, request, pk):
        """
        Update a list by id.
        Collaborators can update lst_pic, is_favorite, is_watched, collaborators, and shows.
        An owner can update lst_name, lst_pic, is_favorite, is_private, is_watched, collaborators, the owner (can cede ownership completely to another user), and shows.
        """
        data = json.loads(request.body)
        lst_name = data.get("lst_name")
        lst_pic = data.get("lst_pic")
        is_favorite = data.get("is_favorite", False)
        is_private = data.get("is_private", False)
        is_watched = data.get("is_watched", False)
        collaborator_ids = data.get("collaborators", [])
        owner_id = data.get("owner", request.user.id)
        show_ids = data.get("shows", [])

        if not Lst.objects.filter(pk=pk):
            return failure_response(f"No list to be found with id of {pk}.")
        lst = Lst.objects.get(pk=pk)

        profile = Profile.objects.get(user=request.user)
        if not profile:
            return failure_response(f"No user to be found with id of {request.user.id}.")

        user_is_collaborator = profile in lst.collaborators.all()
        user_is_owner = profile == lst.owner

        if not (user_is_collaborator or user_is_owner):
            return failure_response(f"User {request.user} does not have the credentials to list of id {pk}.")
        if user_is_owner:
            lst.lst_name = lst_name
            lst.lst_pic = lst_pic
            lst.is_favorite = is_favorite
            lst.is_private = is_private
            lst.is_watched = is_watched
            lst.collaborators.clear()
            for c_id in collaborator_ids:
                if User.objects.filter(pk=c_id):
                    collaborator = User.objects.get(pk=c_id)
                    if Profile.objects.filter(user=collaborator):
                        c = Profile.objects.get(user=collaborator)
                        lst.collaborators.add(c)
            owner_user = User.objects.get(pk=owner_id)
            owner_profile = Profile.objects.get(user=owner_user)
            lst.owner = owner_profile
            lst.shows.clear()
            for show_id in show_ids:
                if Show.objects.filter(pk=show_id):
                    show = Show.objects.get(pk=show_id)
                    lst.shows.add(show)
        elif user_is_collaborator:
            lst.lst_pic = lst_pic
            lst.is_favorite = is_favorite
            lst.is_watched = is_watched
            lst.collaborators.clear()
            for c_id in collaborator_ids:
                if User.objects.filter(pk=c_id):
                    collaborator = User.objects.get(pk=c_id)
                    if Profile.objects.filter(user=collaborator):
                        c = Profile.objects.get(user=collaborator)
                        lst.collaborators.add(c)
            lst.shows.clear()
            for show_id in show_ids:
                if Show.objects.filter(pk=show_id):
                    show = Show.objects.get(pk=show_id)
                    lst.shows.add(show)
        lst.save()
        profile.save()
        serializer = LstSerializer(lst)
        return success_response(serializer.data)
