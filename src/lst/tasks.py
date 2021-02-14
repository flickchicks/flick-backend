from __future__ import absolute_import
from __future__ import unicode_literals

from user.models import Profile

from celery import shared_task
from django.contrib.auth.models import User
from group.models import Group
from lst.models import Lst
from notification.models import Notification
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice
import tmdbsimple as tmdb


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
            message_body = f"{lst.name} has been modified"
            ios_devices.send_message(message={"title": message_title, "body": message_body})
            android_devices.send_message(message={"title": message_title, "body": message_body})
        except:
            continue
    return


@shared_task
def create_new_group_notif(profile_id, group_id, member_ids):
    from_user = User.objects.get(profile__id=profile_id)
    from_profile = Profile.objects.get(id=profile_id)
    for user_id in member_ids:
        # don't notify the group creator
        if user_id == from_user.id:
            continue
        try:
            to_user = User.objects.get(id=user_id)
            to_profile = User.objects.get(user__id=user_id)
            notif = Notification()
            notif.notif_type = "group_invite"
            notif.from_user = from_profile
            notif.to_user = to_profile
            notif.group = Group.objects.get(id=group_id)
            notif.save()
            ios_devices = APNSDevice.objects.filter(user=to_user, active=True)
            android_devices = GCMDevice.objects.filter(user=to_user, active=True)
            message_title = f"{from_user.username} added you to a group"
            message_body = "Decide what to watch together 😊"
            ios_devices.send_message(message={"title": message_title, "body": message_body})
            android_devices.send_message(message={"title": message_title, "body": message_body})
        except:
            continue
