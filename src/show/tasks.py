from celery import shared_task
from django.contrib.auth.models import User
from lst.models import Lst
from show.models import Show


@shared_task
def add_show_to_lsts(show_id, list_ids, user_id):
    user = User.objects.get(id=user_id)
    show = Show.objects.get(pk=show_id)
    for lst in Lst.objects.filter(id__in=list_ids).prefetch_related("collaborators", "owner", "shows"):
        user_profile = user.profile
        is_owner = user_profile == lst.owner
        is_collaborator = lst.collaborators.filter(user=user).exists()
        if not is_owner and not is_collaborator:
            continue
        print("??")
        lst.shows.add(show)
        lst.save()
    return
