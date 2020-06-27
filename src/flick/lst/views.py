from django.contrib.auth.models import User
from django.conf import settings as dj_settings
from django.shortcuts import render

from rest_framework import generics, mixins, status, viewsets
from rest_framework.response import Response

from .models import Lst
from .serializers import LstSerializer
from api import settings as api_settings
from api.utils import failure_response, success_response
from show.models import Show
from user.models import Profile

import json
import re


class LstList(generics.ListCreateAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def list(self, request):
        self.serializer_class = LstSerializer
        return super(LstList, self).list(request)

    def post(self, request):
        data = json.loads(request.body)
        lst_name = data.get("lst_name")
        is_favorite = data.get("is_favorite", False)
        is_private = data.get("is_private", False)
        is_watched = data.get("is_watched", False)
        collaborator_ids = data.get("collaborators", [])
        show_ids = data.get("shows", [])

        lst = Lst()
        lst.lst_name = lst_name
        lst.is_favorite = is_favorite
        lst.is_private = is_private
        lst.is_watched = is_watched
        lst.owner = request.user
        lst.save()

        for collaborator_id in collaborator_ids:
            if User.objects.filter(pk=collaborator_id):
                collaborator = User.objects.get(pk=collaborator_id)
                lst.collaborators.add(collaborator)
                # collaborator_profile = Profile.objects.get(user=collaborator)
                # collaborator_profile.collab_lsts.add(lst)
        for show_id in show_ids:
            if Show.objects.filter(pk=show_id):
                show = Show.objects.get(pk=show_id)
                lst.shows.add(show)
        lst.save()
        serializer = LstSerializer(lst)
        profile = Profile.objects.get(user=request.user)
        profile.owner_lsts.add(lst)
        profile.save()
        return success_response(serializer.data)


class LstDetail(generics.GenericAPIView):

    queryset = Lst.objects.all()
    serializer_class = LstSerializer

    permission_classes = api_settings.UNPROTECTED

    def get(self, request, pk):
        print("ITS HERE AT GET")
        queryset = self.get_object()
        serializer = LstSerializer(queryset, many=False)
        return success_response(serializer.data)

    def delete(self, request, pk):
        print("reached delete")
        return success_response("hi")

    # TODO: need to make the relationships such that
    # the collab_lsts match to wherever Lst has the user as collaborators
    # the owner_lsts match to wherever the Lst has the user as an owner
    def post(self, request, pk):
        print("trying to update")
        data = json.loads(request.body)
        lst_name = data.get("lst_name")
        is_favorite = data.get("is_favorite", False)
        is_private = data.get("is_private", False)
        is_watched = data.get("is_watched", False)
        owner_id = data.get("owner")
        collaborator_ids = data.get("collaborators", [])
        show_ids = data.get("shows", [])

        if not Lst.objects.filter(pk=pk):
            return failure_response(f"No list found with id of {pk} for user {request.user}.")

        lst = Lst.objects.get(id=pk)

        profile = Profile.objects.get(user=request.user)

        test = Lst.objects.filter(collaborators=profile)

        # if lst.collaborators.filter()

        if not (profile in lst.collaborators.all() or lst.owner == profile):
            return failure_response(
                f"User {request.user} is neither a collaborator nor owner, and cannot modify this list of id {pk}."
            )
        elif lst.owner == request.user:
            # only the owner can set public/private settings and change ownership to someone else
            lst.is_private = is_private
            lst.owner = User.objects.get(pk=owner_id)
            lst.save()
            # profile = Profile.objects.get(user=request.user)
            # profile.owner_lsts.add(lst)
            # profile.save()
        # both owner and collaborator have the following permissions:
        lst.is_favorite = is_favorite
        lst.is_watched = is_watched
        lst.lst_name = lst_name
        # clear the collaborators
        lst.collaborators.clear()
        for collaborator_id in collaborator_ids:
            if User.objects.filter(pk=collaborator_id):
                collaborator = User.objects.get(pk=collaborator_id)
                lst.collaborators.add(collaborator)
                # collaborator_profile = Profile.objects.get(user=collaborator)
                # collaborator_profile.collab_lsts.add(lst)
        for show_id in show_ids:
            if Show.objects.filter(pk=show_id):
                show = Show.objects.get(pk=show_id)
                lst.shows.add(show)
        lst.save()
        serializer = LstSerializer(lst)
        return success_response(serializer.data)
        return success_response(test)
