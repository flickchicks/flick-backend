from __future__ import absolute_import
from __future__ import unicode_literals

from user.models import Profile

from celery import shared_task
from django.contrib.auth.models import User
from friendship.models import Friend
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice
from show.models import Show

from .models import PrivateSuggestion


@shared_task
def create_suggestion_and_push_notify(data, profile_id):
    user = User.objects.get(profile__id=profile_id)
    show = Show.objects.get(id=data.get("show_id"))
    profile = Profile.objects.get(id=profile_id)
    for friend_id in data.get("users"):
        try:
            if friend_id == user.pk:
                raise Exception("Unable to suggest to yourself")
            if not User.objects.filter(id=friend_id):
                raise Exception(f"Friend ID {friend_id} does not correspond to a valid user")
            friend = User.objects.get(id=friend_id)
            if not Friend.objects.are_friends(user, friend):
                raise Exception(f"Unable to suggest to non-friend user {friend_id}")
            friend_profile = Profile.objects.get(user=friend)
            if PrivateSuggestion.objects.filter(
                from_user=profile, to_user=friend_profile, show=show, message=data.get("message")
            ):
                continue
            pri_suggestion = PrivateSuggestion()
            pri_suggestion.from_user = profile
            pri_suggestion.to_user = friend_profile
            pri_suggestion.show = show
            pri_suggestion.message = data.get("message")
            pri_suggestion.save()
            ios_devices = APNSDevice.objects.filter(user=friend, active=True)
            android_devices = GCMDevice.objects.filter(user=friend, active=True)
            message_body = f"🎬 {user.first_name} (@{user.username}) suggested {show.title} for you."
            ios_devices.send_message(message={"title": "Telie", "body": message_body})
            android_devices.send_message(message={"title": "Telie", "body": message_body})
        except Exception:
            continue

    return
