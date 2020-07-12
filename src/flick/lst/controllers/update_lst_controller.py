from user.models import Profile

from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User
from lst.models import Lst
from show.models import Show
from tag.models import Tag


class UpdateLstController:
    def __init__(self, request, pk, data, serializer):
        self._request = request
        self._pk = pk
        self._data = data
        self._serializer = serializer
        self._user = request.user
        self._lst = None

    def _add_tags(self, tag_ids):
        self._lst.custom_tags.clear()
        for tag_id in tag_ids:
            if Tag.objects.filter(pk=tag_id):
                tag = Tag.objects.get(pk=tag_id)
                if tag not in self._lst.tags.all():
                    self._lst.custom_tags.add(tag)

    def _add_shows(self, show_ids):
        self._lst.shows.clear()
        for show_id in show_ids:
            if Show.objects.filter(pk=show_id):
                show = Show.objects.get(pk=show_id)
                self._lst.shows.add(show)

    def _add_collaborators(self, collaborator_ids):
        self._lst.collaborators.clear()
        for c_id in collaborator_ids:
            if User.objects.filter(pk=c_id):
                collaborator = User.objects.get(pk=c_id)
                if Profile.objects.filter(user=collaborator):
                    c = Profile.objects.get(user=collaborator)
                    self._lst.collaborators.add(c)

    def process(self):
        lst_name = self._data.get("lst_name")
        lst_pic = self._data.get("lst_pic")
        is_private = self._data.get("is_private", False)
        collaborator_ids = self._data.get("collaborators", [])
        owner_id = self._data.get("owner", self._user.id)
        show_ids = self._data.get("shows", [])
        tag_ids = self._data.get("tags", [])

        if not Lst.objects.filter(pk=self._pk):
            return failure_response(f"No list to be found with id of {self._pk}.")
        self._lst = Lst.objects.get(pk=self._pk)

        if not Profile.objects.filter(user=self._user):
            return failure_response(f"No user to be found with id of {self._user.id}.")
        profile = Profile.objects.get(user=self._user)

        user_is_owner = profile == self._lst.owner
        user_is_collaborator = profile in self._lst.collaborators.all()
        if not (user_is_owner or user_is_collaborator):
            return failure_response(f"User {self._user} does not have the credentials to list of id {self._pk}.")

        if user_is_owner:
            self._lst.is_private = is_private
            self._add_shows(show_ids)
            if not (self._lst.is_saved or self._lst.is_watch_later):
                self._lst.lst_name = lst_name
                self._lst.lst_pic = lst_pic
                self._add_collaborators(collaborator_ids)
                self._add_tags(tag_ids)
                owner_user = User.objects.get(pk=owner_id)
                owner_profile = Profile.objects.get(user=owner_user)
                self._lst.owner = owner_profile

        elif user_is_collaborator:
            self._lst.lst_pic = lst_pic
            self._add_collaborators(collaborator_ids)
            self._add_shows(show_ids)
            self._add_tags(tag_ids)

        self._lst.save()
        return success_response(self._serializer(self._lst).data)
