from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    def collaborators_added_list(self, obj):
        return ", ".join([c.user.username for c in obj.collaborators_added.all()])

    def collaborators_removed_list(self, obj):
        return ", ".join([c.user.username for c in obj.collaborators_removed.all()])

    list_display = [
        "notif_type",
        "from_user",
        "to_user",
        "lst",
        "group",
        "comment",
        "num_shows_added",
        "num_shows_removed",
        "created_at",
        "new_owner",
        "collaborators_added_list",
        "collaborators_removed_list",
    ]


admin.site.register(Notification, NotificationAdmin)
