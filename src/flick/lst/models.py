from asset.models import AssetBundle
from django.contrib.auth.models import User
from django.db import models

from show.models import Show


class Lst(models.Model):
    lst_name = models.CharField(max_length=100)
    lst_pic = models.ForeignKey(AssetBundle, on_delete=models.CASCADE, blank=True, null=True)
    is_favorite = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    is_watched = models.BooleanField(default=False)
    collaborators = models.ManyToManyField(User, related_name="collaborators", blank=True)
    owner = models.ForeignKey(User, related_name="owner", on_delete=models.CASCADE)
    shows = models.ManyToManyField(Show, blank=True)

    @property
    def show_tags(self):
        pass

    @property
    def show_titles(self):
        return ", ".join([s.title for s in self.shows.all()])

    @property
    def poster_pics(self):
        return [s.poster_pic for s in self.shows.all()]
