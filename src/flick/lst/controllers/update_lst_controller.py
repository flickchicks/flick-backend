from user.models import Profile

from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User
from django.db.models import Q
from friendship.models import Friend
from lst.models import Lst
from notification.models import Notification
from show.models import Show
from tag.models import Tag


class UpdateLstController:
    def __init__(self, request, pk, data, serializer, is_add=False, is_remove=False):
        self._request = request
        self._pk = pk
        self._data = data
        self._serializer = serializer
        self._user = request.user
        self._lst = None
        self._profile = None
        self._is_add = is_add
        self._is_remove = is_remove

    def _should_clear(self):
        return not (self._is_add or self._is_remove)

    def _notify_collaborator(self, profile):
        notif = Notification()
        notif.notif_type = "list_invite"
        notif.from_user = self._profile
        notif.to_user = profile
        notif.lst = self._lst
        notif.save()
        return notif

    def _modify_tags(self, tag_ids):
        if self._should_clear():
            self._lst.custom_tags.clear()
        for tag_id in tag_ids:
            if Tag.objects.filter(pk=tag_id):
                tag = Tag.objects.get(pk=tag_id)
                if self._is_remove:
                    self._lst.custom_tags.remove(tag)
                elif tag not in self._lst.tags.all():
                    self._lst.custom_tags.add(tag)

    def _modify_shows(self, show_ids):
        if self._should_clear():
            self._lst.shows.clear()
        for show_id in show_ids:
            if Show.objects.filter(pk=show_id):
                show = Show.objects.get(pk=show_id)
                if self._is_remove:
                    self._lst.shows.remove(show)
                else:
                    self._lst.shows.add(show)

    def _modify_collaborators(self, collaborator_ids):
        old_collaborators = self._lst.collaborators.all()
        if self._should_clear():
            self._lst.collaborators.clear()
        for c_id in collaborator_ids:
            if User.objects.filter(pk=c_id):
                collaborator = User.objects.get(pk=c_id)
                collaborator_friend = Friend.objects.filter(
                    Q(to_user=self._user, from_user=collaborator) | Q(to_user=collaborator, from_user=self._user)
                )
                if not collaborator_friend:
                    continue
                if Profile.objects.filter(user=collaborator):
                    c = Profile.objects.get(user=collaborator)
                    if c not in old_collaborators:
                        self._notify_collaborator(profile=c)
                    if self._is_remove:
                        self._lst.collaborators.remove(c)
                    else:
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
        self._profile = Profile.objects.get(user=self._user)

        user_is_owner = self._profile == self._lst.owner
        user_is_collaborator = self._profile in self._lst.collaborators.all()
        if not (user_is_owner or user_is_collaborator):
            return failure_response(f"User {self._user} does not have the credentials to list of id {self._pk}.")

        if user_is_owner:
            self._lst.is_private = is_private
            self._modify_shows(show_ids)
            self._modify_tags(tag_ids)
            if not (self._lst.is_saved or self._lst.is_watch_later):
                self._lst.lst_name = lst_name
                self._lst.lst_pic = lst_pic
                self._modify_collaborators(collaborator_ids)
                owner_user = User.objects.get(pk=owner_id)
                owner_profile = Profile.objects.get(user=owner_user)
                self._lst.owner = owner_profile

        elif user_is_collaborator:
            self._lst.lst_pic = lst_pic
            self._modify_collaborators(collaborator_ids)
            self._modify_shows(show_ids)
            self._modify_tags(tag_ids)

        self._lst.save()
        return success_response(self._serializer(self._lst).data)
