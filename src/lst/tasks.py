from __future__ import absolute_import
from __future__ import unicode_literals

from user.models import Profile

from celery import shared_task
from django.contrib.auth.models import User
from lst.models import Lst
from notification.models import Notification
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice


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
        ios_devices = APNSDevice.objects.filter(user=to_profile.user, active=True)
        android_devices = GCMDevice.objects.filter(user=to_profile.user, active=True)
        message_title = "Telie"
        message_body = f"📌 {from_profile.user.first_name} (@{from_profile.user.username}) updated {lst.name}."
        ios_devices.send_message(message={"title": message_title, "body": message_body})
        android_devices.send_message(message={"title": message_title, "body": message_body})
