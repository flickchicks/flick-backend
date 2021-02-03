from django.db import models


class Provider(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    image = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ("name", "image")
