from user.models import Profile

from django.db import models
from django.utils.translation import gettext_lazy as _
from show.models import Show


class Vote(models.Model):
    class VoteType(models.TextChoices):
        YES = "Y", _("yes")
        NO = "N", _("no")
        MAYBE = "M", _("maybe")

    voter = models.OneToOneField(Profile, on_delete=models.CASCADE)
    choice = models.CharField(max_length=1, choices=VoteType.choices, null=True, blank=True)
    show = models.OneToOneField(Show, on_delete=models.CASCADE)
