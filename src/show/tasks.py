from user.models import Profile

from celery import shared_task
from lst.models import Lst
from show.models import Show


@shared_task
def add_show_to_lists(show_id, list_ids, user):
    if not Show.objects.filter(pk=show_id):
        raise Exception(f"show with id {show_id} does not exist")
    show = Show.objects.get(pk=show_id)
    success_lists = []
    for lst_id in list_ids:
        lst = Lst.objects.filter(pk=lst_id)
        if lst:
            lst = Lst.objects.get(pk=lst_id)
            user_profile = Profile.objects.get(user=user)
            is_owner = user_profile == lst.owner
            is_collaborator = user_profile in lst.collaborators.all()
            if not is_owner and not is_collaborator:
                continue
            lst.shows.add(show)
            success_lists.append(lst)

    return
