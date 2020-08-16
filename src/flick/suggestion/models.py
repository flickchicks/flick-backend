from user.models import Profile

from django.contrib.auth.models import User
from django.db import models
from show.models import Show


class PublicSuggestion(models.Model):
    author = models.ForeignKey(Profile, related_name="suggestions_posted", on_delete=models.CASCADE)
    message = models.CharField(max_length=140, blank=True)
    show = models.ForeignKey(Show, related_name="suggestion_post", blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)


class PrivateSuggestion(models.Model):
    to_user = models.ForeignKey(User, related_name="suggestions_received", on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, related_name="suggestions_sent", on_delete=models.CASCADE)
    message = models.CharField(max_length=140, blank=True)
    show = models.ForeignKey(Show, related_name="suggestion", blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["message", "show", "from_user", "to_user"]
        ordering = ["-created_at"]
