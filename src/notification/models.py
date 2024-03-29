from user.models import Profile

from comment.models import Comment
from django.db import models
from group.models import Group
from lst.models import Lst
from suggestion.models import PrivateSuggestion


class Notification(models.Model):
    NOTIF_TYPE_CHOICES = (
        ("list_invite", "List Invite"),
        ("list_edit", "List Edit"),
        ("incoming_friend_request_accepted", "Incoming Friend Request Accepted"),
        ("outgoing_friend_request_accepted", "Outoing Friend Request Accepted"),
        ("comment_like", "Comment Like"),
        ("list_like", "List Like"),
        ("suggestion_like", "Suggestion Like"),
        ("group_invite", "Group Invite"),
    )

    notif_type = models.CharField(max_length=50, choices=NOTIF_TYPE_CHOICES, default=None)
    from_user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="sent_notification"
    )
    to_user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="received_notification"
    )
    lst = models.ForeignKey(Lst, on_delete=models.CASCADE, blank=True, null=True, related_name="notification")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, related_name="notification")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True, related_name="notification")
    suggestion = models.ForeignKey(
        PrivateSuggestion, on_delete=models.CASCADE, blank=True, null=True, related_name="notification"
    )
    num_shows_added = models.IntegerField(blank=True, null=True)
    num_shows_removed = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    new_owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="newly_owned_lst_notification"
    )
    collaborators_added = models.ManyToManyField(Profile, blank=True, related_name="added_to_lst_notification")
    collaborators_removed = models.ManyToManyField(Profile, blank=True, related_name="removed_from_lst_notification")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notif_type}, {self.created_at}"
