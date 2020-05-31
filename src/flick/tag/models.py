from django.db import models


class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    # shows = models.ManyToManyField(Show, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
