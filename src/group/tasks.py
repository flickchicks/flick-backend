from __future__ import absolute_import
from __future__ import unicode_literals

import json
from user.models import Profile

from celery import shared_task
from django.contrib.auth.models import User
from group.models import Group
from notification.models import Notification
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice
import tmdbsimple as tmdb
from vote.models import Vote
from vote.models import VoteType


@shared_task
def clear_shows(user_id, group_id):
    profile = Profile.objects.get(user__id=user_id)
    group = profile.groups.get(id=group_id)
    group.shows.clear()
    group.votes.clear()
    return


@shared_task
def vote(request_body, user_id, group_id, show_id):
    profile = Profile.objects.get(user__id=user_id)
    group = profile.groups.get(id=group_id)
    show = group.shows.get(id=show_id)
    data = json.loads(request_body)
    vote_str = data.get("vote")
    if vote_str == "yes":
        choice = VoteType.YES
    elif vote_str == "maybe":
        choice = VoteType.MAYBE
    elif vote_str == "no":
        choice = VoteType.NO
    else:
        return
    vote_exists = group.votes.filter(voter=profile, choice=choice, show=show)
    if vote_exists:
        return
    old_vote = group.votes.filter(voter=profile, show=show)
    if old_vote:
        vote = group.votes.get(voter=profile, show=show)
        vote.choice = choice
        vote.save()
        group.save()
    else:
        vote = Vote.objects.create(voter=profile, choice=choice, show=show)
        group.votes.add(vote)
        group.save()
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
