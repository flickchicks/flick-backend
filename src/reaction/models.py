from user.models import Profile

from django.db import models
from episode_detail.models import EpisodeDetail


class VisibilityChoice(models.TextChoices):
    """Currently a little hacky because the key should be p and value should be public to save
    space in the database. But, Alanna hasn't been able to figure out a way to serialize the value
    (label) properly.
    """

    PUBLIC = u"public", "p"
    FRIENDS = u"friends", "f"


class Reaction(models.Model):
    episode = models.ForeignKey(EpisodeDetail, related_name="reactions", on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    author = models.ForeignKey(Profile, related_name="reaction", on_delete=models.CASCADE)
    visibility = models.CharField(max_length=20, choices=VisibilityChoice.choices, default=VisibilityChoice.PUBLIC)
    num_likes = models.IntegerField(default=0, null=True)
