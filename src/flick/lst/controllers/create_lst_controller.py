from user.models import Profile

from api.utils import success_response
from django.contrib.auth.models import User
from lst.models import Lst
from show.models import Show


class CreateLstController:
    def __init__(self, request, data, serializer):
        self._request = request
        self._data = data
        self._serializer = serializer

    def process(self):
        lst_name = self._data.get("lst_name")
        lst_pic = self._data.get("lst_pic")
        is_private = self._data.get("is_private", False)
        collaborator_ids = self._data.get("collaborators", [])
        show_ids = self._data.get("shows", [])

        lst = Lst()
        lst.lst_name = lst_name
        lst.lst_pic = lst_pic
        lst.is_private = is_private
        profile = Profile.objects.get(user=self._request.user)
        lst.owner = profile
        lst.save()

        for c_id in collaborator_ids:
            collaborator = User.objects.filter(pk=c_id)
            if not collaborator:
                continue
            if Profile.objects.filter(user=collaborator):
                c = Profile.objects.get(user=collaborator)
                lst.collaborators.add(c)
        for show_id in show_ids:
            if Show.objects.filter(pk=show_id):
                show = Show.objects.get(pk=show_id)
                lst.shows.add(show)
        lst.save()
        return success_response(self._serializer(lst).data)
