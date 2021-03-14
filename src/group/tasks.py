from __future__ import absolute_import
from __future__ import unicode_literals

from itertools import chain
import json
from random import sample
from user.models import Profile

from celery import shared_task
from django.contrib.auth.models import User
from django.core.cache import caches
from group.models import Group
from lst.models import Lst
from notification.models import Notification
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice
from show.models import Show
from show.show_api_utils import ShowAPI
from show.tmdb import flicktmdb
import tmdbsimple as tmdb
from vote.models import Vote
from vote.models import VoteType

local_cache = caches["local"]


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
            to_profile = Profile.objects.get(user__id=user_id)
            notif = Notification()
            notif.notif_type = "group_invite"
            notif.from_user = from_profile
            notif.to_user = to_profile
            notif.group = Group.objects.get(id=group_id)
            notif.save()
            ios_devices = APNSDevice.objects.filter(user=to_user, active=True)
            android_devices = GCMDevice.objects.filter(user=to_user, active=True)
            message_body = f"🤩 {from_user.first_name} (@{from_user.username}) added you to a group."
            ios_devices.send_message(message={"title": "Telie", "body": message_body})
            android_devices.send_message(message={"title": "Telie", "body": message_body})
        except Exception:
            continue


@shared_task
def add_shows_to_group(user, group_id, show_ids, num_random_shows):
    profile = user.profile
    group = profile.groups.get(id=group_id)
    api = flicktmdb()
    for show_id in show_ids:
        try:
            show = Show.objects.get(id=show_id)
            group.shows.add(show)
        except:
            continue
    rec_shows = []
    if num_random_shows > 0:
        show_lst = []
        lsts = Lst.objects.filter(is_private=False, owner__in=group.members.all()).prefetch_related("shows")
        show_lst = [lst.shows.filter(ext_api_source="tmdb") for lst in lsts]
        shows = list(chain.from_iterable(show_lst))
        shows = sample(shows, min(5, len(shows)))
        for show in group.shows.filter(ext_api_source="tmdb"):
            shows.append(show)

        for show in shows:
            if not show:
                continue
            similar = local_cache.get((show.id, "similar"))
            if not similar:
                similar = api.get_similar_shows(show.ext_api_id, show.is_tv)
                local_cache.set((show.id, "similar"), similar)
            rec_shows.extend(similar)

        if len(rec_shows) < num_random_shows:
            rec_shows.extend(api.get_trending_shows())
        data = ShowAPI.create_show_objects_no_serialization(rec_shows)
        rec_shows = sample(data, num_random_shows)

    for rec_show in rec_shows:
        group.shows.add(rec_show)
    group.save()

    return


@shared_task
def remove_shows_from_group(user, group_id, show_ids):
    group = user.profile.groups.get(id=group_id)
    for show_id in show_ids:
        try:
            show = Show.objects.get(id=show_id)
            group.shows.remove(show)
        except:
            continue
    group.save()
    return
