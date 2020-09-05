from user.models import Profile

from comment.models import Comment
from django.db import models


class Read(models.Model):
    reader = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="read_comments")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reads")
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["reader", "comment"]
        ordering = ["-created_at"]
