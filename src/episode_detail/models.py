from django.db import models
from season_detail.models import SeasonDetail


class EpisodeDetail(models.Model):
    DEFAULT_EPISODE_NUM = 1
    ext_api_id = models.IntegerField(blank=True, null=True)  # will assume its parent show's ext_api_source
    is_default = models.BooleanField(default=False, blank=True, null=True)
    season = models.ForeignKey(SeasonDetail, related_name="episode_details", on_delete=models.CASCADE)
    episode_num = models.IntegerField(default=DEFAULT_EPISODE_NUM, blank=True, null=True)
    name = models.TextField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("season", "episode_num")
