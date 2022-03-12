from user.models import Profile

from django.db import models
from reaction.models import Reaction


class Thought(models.Model):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE, related_name="thoughts")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="thought")
    num_likes = models.IntegerField(default=0, null=True)
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-num_likes"]

    def __str__(self):
        return self.message
