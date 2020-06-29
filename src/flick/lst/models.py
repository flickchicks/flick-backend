from asset.models import AssetBundle
from django.contrib.auth.models import User
from django.db import models

from show.models import Show
from user.models import Profile


class Lst(models.Model):
    lst_name = models.CharField(max_length=100)
    lst_pic = models.TextField(blank=True, null=True)
    # lst_asset_bundle = models.ForeignKey(AssetBundle, on_delete=models.CASCADE, blank=True, null=True)
    is_favorite = models.BooleanField(default=False, null=True)
    is_private = models.BooleanField(default=False, null=True)
    is_watched = models.BooleanField(default=False, null=True)
    collaborators = models.ManyToManyField(Profile, related_name="collab_lsts", blank=True)
    owner = models.ForeignKey(Profile, related_name="owner_lsts", on_delete=models.CASCADE)
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

    def upload_lst_pic(self):
        pass  # TODO: look at upload_profile_pic in user models
