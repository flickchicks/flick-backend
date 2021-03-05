from user.models import Profile

from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User
from friendship.models import Friend
from lst.models import Lst
from lst.models import LstSaveActivity
from notification.models import Notification
from show.models import Show
from tag.models import Tag

from ..tasks import create_lst_edit_notif
from ..tasks import create_modified_collaborators_notif


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
        from_profile_id = self._profile.id
        to_profile_ids = [p.id for p in self._profiles_to_notify]
        create_lst_edit_notif.delay(
            from_profile_id=from_profile_id,
            to_profile_ids=to_profile_ids,
            lst_id=self._lst.id,
            num_modified_shows=len(modified_shows),
            is_add=self._is_add,
            is_remove=self._is_remove,
        )

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
        from_profile_id = self._profile.id
        to_profile_ids = [p.id for p in self._profiles_to_notify]
        create_modified_collaborators_notif.delay(
            from_profile_id=from_profile_id,
            to_profile_ids=to_profile_ids,
            modified_profile_ids=[m.id for m in modified_collaborators],
            lst_id=self._lst.id,
            is_add=self._is_add,
            is_remove=self._is_remove,
        )

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
                    activity = self._lst.activity.get(show=show)
                    activity.delete()
                    modified_shows.append(show)
                else:
                    self._lst.shows.add(show)
                    if not show.activity.filter(lst=self._lst):
                        lst_activity = LstSaveActivity()
                        lst_activity.show = show
                        lst_activity.saved_by = self._profile
                        lst_activity.lst = self._lst
                        lst_activity.save()
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
            c_is_friend = Friend.objects.are_friends(self._user, c)
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
        description = self._data.get("description")
        is_private = self._data.get("is_private", False)
        collaborator_ids = self._data.get("collaborators", [])
        owner_id = self._data.get("owner", self._user.id)
        show_ids = self._data.get("shows", [])
        tag_ids = self._data.get("tags", [])

        if not Lst.objects.filter(pk=self._pk):
            return failure_response(f"No list to be found with id of {self._pk}.")
        self._lst = Lst.objects.get(pk=self._pk)
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
                if name:
                    self._lst.name = name
                if description:
                    self._lst.description = description
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
        return success_response(self._serializer(self._lst, context={"request": self._request}).data)
