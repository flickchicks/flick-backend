from user.models import Profile

from comment.models import Comment
from django.db import models
from lst.models import Lst
from reaction.models import Reaction
from suggestion.models import PrivateSuggestion
from thought.models import Thought


class Like(models.Model):
    LIKE_TYPE_CHOICES = (
        ("comment_like", "Comment Like"),
        ("list_like", "List Like"),
        ("suggestion_like", "Suggestion Like"),
        ("reaction_like", "Reaction Like"),
        ("thought_like", "Thought Like"),
    )
    like_type = models.CharField(max_length=50, choices=LIKE_TYPE_CHOICES, default="comment_like")
    liker = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    lst = models.ForeignKey(Lst, on_delete=models.CASCADE, blank=True, null=True, related_name="likers")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True, related_name="likers")
    suggestion = models.ForeignKey(
        PrivateSuggestion, on_delete=models.CASCADE, blank=True, null=True, related_name="likers"
    )
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE, blank=True, null=True, related_name="likers")
    thought = models.ForeignKey(Thought, on_delete=models.CASCADE, blank=True, null=True, related_name="likers")
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
