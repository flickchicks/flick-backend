from __future__ import absolute_import
from __future__ import unicode_literals

from user.models import Profile

from celery import shared_task
from django.contrib.auth.models import User
from lst.models import Lst
from lst.models import LstSaveActivity
from notification.models import Notification
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice
from show.models import Show


@shared_task
def create_lst_invite_notif(profile_id, lst_id, collaborator_ids):
    from_user = User.objects.get(profile__id=profile_id)
    from_profile = Profile.objects.get(id=profile_id)
    lst = Lst.objects.get(id=lst_id)
    for user_id in collaborator_ids:
        if user_id == from_user.id:
            continue
        try:
            to_user = User.objects.get(id=user_id)
            to_profile = Profile.objects.get(user__id=user_id)
            notif = Notification()
            notif.notif_type = "list_invite"
            notif.from_user = from_profile
            notif.to_user = to_profile
            notif.lst = lst
            notif.save()
            ios_devices = APNSDevice.objects.filter(user=to_user, active=True)
            android_devices = GCMDevice.objects.filter(user=to_user, active=True)
            message_title = "Telie"
            message_body = f"📌 {from_user.first_name} (@{from_user.username}) invited you to collaborate on a list."
            ios_devices.send_message(message={"title": message_title, "body": message_body})
            android_devices.send_message(message={"title": message_title, "body": message_body})
        except:
            continue
    return


@shared_task
def create_lst_edit_notif(from_profile_id, to_profile_ids, lst_id, num_modified_shows, is_add, is_remove):
    if num_modified_shows == 0:
        return
    for to_profile_id in to_profile_ids:
        from_profile = Profile.objects.get(id=from_profile_id)
        to_profile = Profile.objects.get(id=to_profile_id)
        lst = Lst.objects.get(id=lst_id)
        notif = Notification()
        notif.notif_type = "list_edit"
        notif.from_user = from_profile
        notif.to_user = to_profile
        notif.lst = lst
        if is_add:
            notif.num_shows_added = num_modified_shows
        elif is_remove:
            notif.num_shows_removed = num_modified_shows
        notif.save()
        # ios_devices = APNSDevice.objects.filter(user=to_profile.user, active=True)
        # android_devices = GCMDevice.objects.filter(user=to_profile.user, active=True)
        # message_title = "Telie"
        # message_body = (
        #     f"🥳 {from_profile.user.first_name} (@{from_profile.user.username}) updated the shows in {lst.name}."
        # )
        # ios_devices.send_message(message={"title": message_title, "body": message_body})
        # android_devices.send_message(message={"title": message_title, "body": message_body})


@shared_task
def create_modified_collaborators_notif(
    from_profile_id, to_profile_ids, modified_profile_ids, lst_id, is_add, is_remove
):
    if not to_profile_ids:
        return
    from_profile = Profile.objects.get(id=from_profile_id)
    # New collaborators should get an invite
    if is_add:
        for m_p_id in modified_profile_ids:
            to_profile = Profile.objects.get(id=m_p_id)
            ios_devices = APNSDevice.objects.filter(user=to_profile.user, active=True)
            android_devices = GCMDevice.objects.filter(user=to_profile.user, active=True)
            message_title = "Telie"
            message_body = f"📌 {from_profile.user.first_name} (@{from_profile.user.username}) invited you to collaborate on a list."
            ios_devices.send_message(message={"title": message_title, "body": message_body})
            android_devices.send_message(message={"title": message_title, "body": message_body})
    # Notify old collaborators that collaborators have been updated
    # for to_profile_id in to_profile_ids:
    #     to_profile = Profile.objects.get(id=to_profile_id)
    #     lst = Lst.objects.get(id=lst_id)
    #     notif = Notification()
    #     notif.notif_type = "list_edit"
    #     notif.from_user = from_profile
    #     notif.to_user = to_profile
    #     notif.lst = lst
    #     notif.save()
    #     modified_collaborators = Profile.objects.filter(id__in=modified_profile_ids)
    #     if is_add:
    #         notif.collaborators_added.add(*modified_collaborators)
    #     elif is_remove:
    #         notif.collaborators_removed.add(*modified_collaborators)
    #     notif.save()
    #     ios_devices = APNSDevice.objects.filter(user=to_profile.user, active=True)
    #     android_devices = GCMDevice.objects.filter(user=to_profile.user, active=True)
    #     message_title = "Telie"
    #     message_body = (
    #         f"🥳 {from_profile.user.first_name} (@{from_profile.user.username}) updated the collaborators in {lst.name}."
    #     )
    #     ios_devices.send_message(message={"title": message_title, "body": message_body})
    #     android_devices.send_message(message={"title": message_title, "body": message_body})


@shared_task
def modify_lst_shows(user_id, lst_id, show_ids, is_add, is_remove):
    lst = Lst.objects.get(id=lst_id)
    modified_shows = []
    user_profile = Profile.objects.get(user__id=user_id)
    is_owner = user_profile == lst.owner
    is_collaborator = lst.collaborators.filter(user__id=user_id).exists()
    # stop the task if the user does not have edit access
    if not is_owner and not is_collaborator:
        return
    for show in Show.objects.filter(id__in=show_ids).prefetch_related("activity"):
        if is_add:
            if lst.shows.filter(id=show.id).exists():
                return
            lst.shows.add(show)
            if not lst.activity.filter(show=show):
                lst_activity = LstSaveActivity()
                lst_activity.show = show
                lst_activity.saved_by = user_profile
                lst_activity.lst = lst
                lst_activity.save()
        if is_remove:
            lst.shows.remove(show)
            activity = lst.activity.filter(show=show)
            if activity:
                activity[0].delete()
                modified_shows.append(show)
        modified_shows.append(show)
    if not modified_shows:
        return
    # notify the collaborators
    to_profile_ids = list(lst.collaborators.values_list("id", flat=True))
    create_lst_edit_notif.delay(
        from_profile_id=user_id,
        to_profile_ids=to_profile_ids,
        lst_id=lst.id,
        num_modified_shows=len(modified_shows),
        is_add=is_add,
        is_remove=is_remove,
    )
    return
