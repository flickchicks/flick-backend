from user.models import Profile

from django.db import models
from show.models import Show


class Comment(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="comments")
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="comment")
    num_likes = models.IntegerField(default=0, null=True)
    is_spoiler = models.BooleanField(default=False, blank=True, null=True)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = ["owner", "message", "is_spoiler", "show"]

    def __str__(self):
        return self.message
