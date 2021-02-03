from django.contrib.auth.models import User
from django.db import models


class Rating(models.Model):
    rater = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(blank=True, null=True, default=None)
