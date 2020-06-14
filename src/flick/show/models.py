from django.db import models

from tag.models import Tag


class Show(models.Model):
    EXT_API_SOURCE_CHOICES = (("tmdb", "TMDB"), ("animelist", "Animelist"))

    title = models.CharField(max_length=100, null=False, blank=False)
    ext_api_id = models.IntegerField(blank=True, null=True)
    ext_api_source = models.CharField(max_length=20, choices=EXT_API_SOURCE_CHOICES, default=None)
    poster_pic = models.URLField(blank=True, null=True)
    director = models.CharField(max_length=100)
    is_tv = models.BooleanField()
    date_released = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    plot = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="shows", blank=True)
    seasons = models.IntegerField(blank=True, null=True)
    audience_level = models.CharField(max_length=100, blank=True, null=True)
    imdb_rating = models.CharField(max_length=10, blank=True, null=True)
    tomato_rating = models.CharField(max_length=10, blank=True, null=True)
    platforms = models.CharField(max_length=100, blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("title", "ext_api_id", "ext_api_source", "poster_pic")

    @property
    def friends_rating(self):
        return 0
