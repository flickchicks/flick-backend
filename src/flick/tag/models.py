from django.db import models


class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def shows(self):
        return [show.title for show in self.shows.all()]

    @property
    def lsts(self):
        from lst.models import Lst

        return Lst.objects.filter(shows__in=self.shows.all(), is_private=False)
