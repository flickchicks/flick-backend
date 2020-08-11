from user.models import Profile

from django.db import models
from lst.models import Lst


class Notification(models.Model):
    NOTIF_TYPE_CHOICES = (("list_invite", "List Invite"), ("list_edit", "List Edit"))

    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES, default=None)
    from_user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="sent_notification"
    )
    to_user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="received_notification"
    )
    lst = models.ForeignKey(Lst, on_delete=models.CASCADE, blank=True, null=True, related_name="notification")
    num_shows_added = models.IntegerField(blank=True, null=True)
    num_shows_removed = models.IntegerField(blank=True, null=True)
    collaborator_added = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="lst_added_to"
    )
    collaborator_removed = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="lst_removed_from"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.notif_type}, {self.created_at}"