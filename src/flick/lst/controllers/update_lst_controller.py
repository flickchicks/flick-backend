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
        self._old_collaborators = []
        self._profiles_to_notify = []

    def _is_simple_update(self):
        return not (self._is_add or self._is_remove)

    def _notify_collaborator(self, profile):
        if not profile:
            return
        notif = Notification()
        notif.notif_type = "list_invite"
        notif.from_user = self._profile
        notif.to_user = profile
        notif.lst = self._lst
        notif.save()
        return notif

    def _create_edit_notification(self, modified_shows):
        if not modified_shows:
            return
        for profile in self._profiles_to_notify:
            notif = Notification()
            notif.notif_type = "list_edit"
            notif.from_user = self._profile
            notif.to_user = profile
            notif.lst = self._lst
            if self._is_add:
                notif.num_shows_added = len(modified_shows)
            elif self._is_remove:
                notif.num_shows_removed = len(modified_shows)
            notif.save()

    def _create_new_owner_notification(self, owner):
        if not owner:
            return
        for profile in self._profiles_to_notify:
            notif = Notification()
            notif.notif_type = "list_edit"
            notif.from_user = self._profile
            notif.to_user = profile
            notif.lst = self._lst
            notif.new_owner = owner
            notif.save()

    def _create_modified_collaborators_notification(self, modified_collaborators=[]):
        if not modified_collaborators:
            return
        for profile in self._profiles_to_notify:
            notif = Notification()
            notif.notif_type = "list_edit"
            notif.from_user = self._profile
            notif.to_user = profile
            notif.lst = self._lst
            notif.save()
            if self._is_add:
                notif.collaborators_added.add(*modified_collaborators)
            elif self._is_remove:
                notif.collaborators_removed.add(*modified_collaborators)
            notif.save()

    def _modify_tags(self, tag_ids):
        if self._is_simple_update():
            return
        for tag_id in tag_ids:
            if Tag.objects.filter(pk=tag_id):
                tag = Tag.objects.get(pk=tag_id)
                if self._is_remove:
                    self._lst.custom_tags.remove(tag)
                elif tag not in self._lst.tags.all():
                    self._lst.custom_tags.add(tag)

    def _modify_shows(self, show_ids):
        if self._is_simple_update():
            return
        modified_shows = []
        for show_id in show_ids:
            if Show.objects.filter(pk=show_id):
                show = Show.objects.get(pk=show_id)
                if self._is_remove:
                    self._lst.shows.remove(show)
                    modified_shows.append(show)
                else:
                    self._lst.shows.add(show)
                    modified_shows.append(show)
        self._create_edit_notification(modified_shows=modified_shows)

    def _modify_collaborators(self, collaborator_ids):
        if self._is_simple_update():
            return
        modified_collaborators = []
        for c_id in collaborator_ids:
            if not (User.objects.filter(id=c_id) or Profile.objects.filter(user__id=c_id)):
                continue
            c = User.objects.get(id=c_id)
            c_is_friend = Friend.objects.filter(Q(to_user=self._user, from_user=c) | Q(to_user=c, from_user=self._user))
            c = Profile.objects.get(user__id=c_id)
            if self._is_remove and c in self._old_collaborators:
                self._lst.collaborators.remove(c)
                modified_collaborators.append(c)
            elif self._is_add and c_is_friend and c not in self._old_collaborators:
                self._lst.collaborators.add(c)
                modified_collaborators.append(c)
                self._notify_collaborator(c)
        self._create_modified_collaborators_notification(modified_collaborators=modified_collaborators)

    def process(self):
        name = self._data.get("name")
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

        # need to copy; querysets cannot be copied easily
        self._old_collaborators = [Profile.objects.get(pk=c.id) for c in self._lst.collaborators.all()]
        self._profiles_to_notify = self._old_collaborators + [self._lst.owner]

        # don't want to notify yourself
        self._profiles_to_notify.remove(self._profile)

        if user_is_owner:
            self._lst.is_private = is_private
            self._modify_shows(show_ids)
            self._modify_tags(tag_ids)
            if not (self._lst.is_saved or self._lst.is_watch_later):
                self._lst.name = name
                self._lst.lst_pic = lst_pic
                self._modify_collaborators(collaborator_ids)
                if self._user.id != owner_id and Profile.objects.filter(user__id=owner_id):
                    owner = Profile.objects.get(user__id=owner_id)
                    self._create_new_owner_notification(owner)
                    self._lst.owner = owner
        elif user_is_collaborator:
            self._lst.lst_pic = lst_pic
            self._modify_collaborators(collaborator_ids)
            self._modify_shows(show_ids)
            self._modify_tags(tag_ids)

        self._lst.save()
        return success_response(self._serializer(self._lst).data)
