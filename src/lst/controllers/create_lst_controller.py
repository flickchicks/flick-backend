from user.models import Profile

from api.utils import success_response
from django.contrib.auth.models import User
from lst.models import Lst
from show.models import Show
from tag.models import Tag

from ..tasks import create_lst_invite_notif


class CreateLstController:
    def __init__(self, request, data, serializer):
        self._request = request
        self._data = data
        self._serializer = serializer
        self._profile = None
        self._lst = None

    def process(self):
        name = self._data.get("name")
        pic = self._data.get("pic")
        description = self._data.get("description")
        is_private = self._data.get("is_private", False)
        collaborator_ids = self._data.get("collaborators", [])
        show_ids = self._data.get("shows", [])
        tag_ids = self._data.get("tags", [])

        lst = Lst()
        lst.name = name
        lst.pic = pic
        lst.description = description
        lst.is_private = is_private
        self._profile = Profile.objects.get(user=self._request.user)
        lst.owner = self._profile
        lst.save()
        self._lst = lst

        for c_id in collaborator_ids:
            if User.objects.filter(pk=c_id):
                collaborator = User.objects.get(pk=c_id)
                if Profile.objects.filter(user=collaborator):
                    c = Profile.objects.get(user=collaborator)
                    lst.collaborators.add(c)
        create_lst_invite_notif.delay(profile_id=self._profile.id, collaborator_ids=collaborator_ids)
        for show_id in show_ids:
            if Show.objects.filter(pk=show_id):
                show = Show.objects.get(pk=show_id)
                lst.shows.add(show)
        for tag_id in tag_ids:
            if Tag.objects.filter(pk=tag_id):
                tag = Tag.objects.get(pk=tag_id)
                if tag not in lst.tags.all():
                    lst.custom_tags.add(tag)
        lst.save()
        return success_response(self._serializer(lst, context={"request": self._request}).data)
