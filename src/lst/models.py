from user.models import Profile

from django.db import models
from show.models import Show
from tag.models import Tag


class Lst(models.Model):
    name = models.CharField(max_length=100)
    pic = models.TextField(blank=True, null=True)
    # lst_asset_bundle = models.ForeignKey(AssetBundle, on_delete=models.CASCADE, blank=True, null=True)
    is_saved = models.BooleanField(default=False, null=True)
    is_private = models.BooleanField(default=False, null=True)
    is_watch_later = models.BooleanField(default=False, null=True)
    collaborators = models.ManyToManyField(Profile, related_name="collab_lsts", blank=True)
    owner = models.ForeignKey(Profile, related_name="owner_lsts", on_delete=models.CASCADE)
    shows = models.ManyToManyField(Show, blank=True)
    custom_tags = models.ManyToManyField(Tag, related_name="lsts", blank=True)
    description = models.CharField(max_length=150, default="", blank=True, null=True)
    num_likes = models.IntegerField(default=0, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def tags(self):
        show_tags = Tag.objects.filter(shows__in=self.shows.all())
        return show_tags.union(self.custom_tags.all())

    @property
    def show_titles(self):
        return ", ".join([s.title for s in self.shows.all()])

    @property
    def poster_pics(self):
        return [s.poster_pic for s in self.shows.all()]

    def upload_pic(self):
        pass  # TODO: look at upload_profile_pic in user models

    class Meta:
        ordering = ["-updated_at"]
