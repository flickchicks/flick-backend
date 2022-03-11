from django.db import models
from show.models import Show


class SeasonDetail(models.Model):
    DEFAULT_SEASON_NUM = 1

    show = models.ForeignKey(Show, related_name="season_details", on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False, blank=True, null=True)
    season_num = models.IntegerField(default=DEFAULT_SEASON_NUM, blank=True, null=True)
    episode_count = models.IntegerField(blank=True, null=True)
    ext_api_id = models.IntegerField(blank=True, null=True)  # will assume its parent show's ext_api_source
    poster_pic = models.URLField(blank=True, null=True)
    overview = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("show", "season_num")
