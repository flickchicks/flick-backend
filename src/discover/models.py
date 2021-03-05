# Create your models here.
from user.models import Profile

from comment.models import Comment
from django.contrib.auth.models import User
from django.db import models
from lst.models import Lst
from show.models import Show


class Discover(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    friend_recommendations = models.ManyToManyField(Profile, related_name="profile_recommend", blank=True)
    friend_shows = models.ManyToManyField(Show, related_name="friend_show_recommend", blank=True)
    friend_lsts = models.ManyToManyField(Lst, related_name="friend_lst_recommend", blank=True)
    friend_comments = models.ManyToManyField(Comment, related_name="friend_comment", blank=True)
