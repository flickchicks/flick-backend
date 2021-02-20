from django.db import models
from lst.models import Lst
from show.models import Show


class DiscoverRecommendation(models.Model):
    RECOMMEND_TYPE_CHOICES = (
        ("friend_list", "Friend List"),
        ("friend_show", "Friend Show"),
        ("trending_list", "Trending List"),
        ("trending_show", "Trending Show"),
    )
    recommend_type = models.CharField(max_length=50, choices=RECOMMEND_TYPE_CHOICES, default=None)
    lst = models.ForeignKey(Lst, on_delete=models.CASCADE, blank=True, null=True, related_name="recommendation")
    show = models.ForeignKey(Show, on_delete=models.CASCADE, blank=True, null=True, related_name="recommendation")
