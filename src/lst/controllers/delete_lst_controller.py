from user.models import Profile

from api.utils import failure_response
from api.utils import success_response
from lst.models import Lst


class DeleteLstController:
    def __init__(self, request, pk):
        self._request = request
        self._pk = pk

    def process(self):
        if not Lst.objects.filter(pk=self._pk):
            return failure_response(f"List of id {self._pk} does not exist.")
        lst = Lst.objects.get(pk=self._pk)
        if lst.is_saved:
            return failure_response(f"List of id {self._pk} is a default saved list and cannot be deleted.")
        if lst.is_watch_later:
            return failure_response(f"List of id {self._pk} is a default watch later list and cannot be deleted.")
        profile = Profile.objects.get(user=self._request.user)
        if not profile == lst.owner:
            return failure_response(f"User of id {self._request.user.id} is not the owner of list of id {self._pk}.")

        lst.delete()
        return success_response(f"List of id {self._pk} has been deleted.")
