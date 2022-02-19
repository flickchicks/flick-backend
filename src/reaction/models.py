from user.models import Profile

from django.db import models
from episode_detail.models import EpisodeDetail


class Reaction(models.Model):
    episode = models.ForeignKey(EpisodeDetail, related_name="reactions", on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    author = models.ForeignKey(Profile, related_name="reaction", on_delete=models.CASCADE)
