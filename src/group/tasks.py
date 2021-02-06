from __future__ import absolute_import
from __future__ import unicode_literals

import json
from user.models import Profile

from celery import shared_task
import tmdbsimple as tmdb
from vote.models import Vote
from vote.models import VoteType


@shared_task
def clear_shows(user_pk, group_pk):
    profile = Profile.objects.get(user__id=user_pk)
    group = profile.groups.get(id=group_pk)
    group.shows.clear()
    group.votes.clear()
    return


@shared_task
def vote(request_body, user_pk, group_pk, show_pk):
    profile = Profile.objects.get(user__id=user_pk)
    group = profile.groups.get(id=group_pk)
    show = group.shows.get(id=show_pk)
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
