from django.db import models
from provider.models import Provider
from rating.models import Rating
from tag.models import Tag


class Show(models.Model):
    EXT_API_SOURCE_CHOICES = (("tmdb", "TMDB"), ("animelist", "Animelist"))

    title = models.CharField(max_length=500, null=False, blank=False)
    ext_api_id = models.IntegerField(blank=True, null=True)
    ext_api_source = models.CharField(max_length=20, choices=EXT_API_SOURCE_CHOICES, default=None)
    poster_pic = models.URLField(blank=True, null=True)
    backdrop_pic = models.URLField(blank=True, null=True)
    directors = models.CharField(max_length=100, null=True, blank=True)
    cast = models.TextField(null=True, blank=True)
    is_tv = models.BooleanField()
    is_adult = models.BooleanField(blank=True, null=True)
    date_released = models.CharField(max_length=100, blank=True, null=True)  # models.DateField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="shows", blank=True)
    seasons = models.IntegerField(blank=True, null=True)
    episodes = models.IntegerField(blank=True, null=True)
    imdb_rating = models.IntegerField(blank=True, null=True)
    tomato_rating = models.CharField(max_length=10, blank=True, null=True)
    animelist_rating = models.IntegerField(blank=True, null=True)
    animelist_rank = models.IntegerField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ratings = models.ManyToManyField(Rating, blank=True)
    providers = models.ManyToManyField(Provider, blank=True)

    class Meta:
        unique_together = ("title", "ext_api_id", "ext_api_source", "poster_pic")
