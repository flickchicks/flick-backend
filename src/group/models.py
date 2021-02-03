from user.models import Profile

from django.db import models
from show.models import Show
from vote.models import Vote


class Group(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)
    members = models.ManyToManyField(Profile, related_name="groups", blank=True)
    shows = models.ManyToManyField(Show, blank=True)
    votes = models.ManyToManyField(Vote, blank=True)
