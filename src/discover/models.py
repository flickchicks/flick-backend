# Create your models here.
from user.models import Profile

from comment.models import Comment
from discover_recommend.models import DiscoverRecommendation
from django.contrib.auth.models import User
from django.db import models


# class Recommendation(models.Model):
#     RECOMMEND_TYPE_CHOICES = (
#     ("friend_list", "Friend List"),
#     ("friend_show", "Friend Show"),
#     ("trending_list", "Trending List"),
#     ("trending_show", "Trending Show")
#     )
#     recommend_type = models.CharField(max_length=50, choices=RECOMMEND_TYPE_CHOICES, default=None)
#     lst = models.ForeignKey(Lst, on_delete=models.CASCADE, blank=True, null=True, related_name="recommendation")
#     show = models.ForeignKey(Show, on_delete=models.CASCADE, blank=True, null=True, related_name="recommendation")


class Discover(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    friend_recommendations = models.ManyToManyField(Profile, related_name="profile_recommend", blank=True)
    list_recommendations = models.ManyToManyField(DiscoverRecommendation, related_name="list_recommend", blank=True)
    show_recommendations = models.ManyToManyField(DiscoverRecommendation, related_name="show_recommend", blank=True)
    friend_comments = models.ManyToManyField(Comment, related_name="friend_comment", blank=True)
