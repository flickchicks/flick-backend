from user.models import Profile

from comment.models import Comment
from django.db import models
from lst.models import Lst


class Like(models.Model):
    LIKE_TYPE_CHOICES = (
        ("comment_like", "Comment Like"),
        ("list_like", "List Like"),
    )
    like_type = models.CharField(max_length=50, choices=LIKE_TYPE_CHOICES, default="comment_like")
    liker = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    lst = models.ForeignKey(Lst, on_delete=models.CASCADE, blank=True, null=True, related_name="likers")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True, related_name="likers")
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["liker", "comment"]
        ordering = ["-created_at"]
