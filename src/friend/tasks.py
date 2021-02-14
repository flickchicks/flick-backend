from __future__ import absolute_import
from __future__ import unicode_literals

from user.models import Profile

from celery import shared_task
from notification.models import Notification
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice


@shared_task
def create_incoming_friend_request_accepted_for_to_user(from_user, to_user):
    from_profile = Profile.objects.get(user=from_user)
    to_profile = Profile.objects.get(user=to_user)
    notif = Notification()
    notif.notif_type = "incoming_friend_request_accepted"
    notif.from_user = from_profile
    notif.to_user = to_profile
    notif.save()


@shared_task
def create_outgoing_friend_request_accepted_for_from_user(from_user, to_user):
    from_profile = Profile.objects.get(user=from_user)
    to_profile = Profile.objects.get(user=to_user)
    notif = Notification()
    notif.notif_type = "outgoing_friend_request_accepted"
    notif.from_user = to_profile
    notif.to_user = from_profile
    notif.save()
    ios_devices = APNSDevice.objects.filter(user=from_user, active=True)
    android_devices = GCMDevice.objects.filter(user=from_user, active=True)
    message_body = f"({from_user.username}): {to_user.first_name} (@{to_user.username}) accepted your friend request."
    ios_devices.send_message(message={"body": message_body})
    android_devices.send_message(message={"body": message_body})
