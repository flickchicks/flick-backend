from user.models import Profile

from comment.models import Comment
from django.db import models


class Like(models.Model):
    liker = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likers")
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["liker", "comment"]
        ordering = ["-created_at"]
