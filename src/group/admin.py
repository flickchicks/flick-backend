from django.contrib import admin

from .models import Group


class GroupAdmin(admin.ModelAdmin):
    def members_list(self, obj):
        return ", ".join([m.user.username for m in obj.members.all()])

    def shows_list(self, obj):
        return ", ".join([s.title for s in obj.shows.all()])

    def votes_list(self, obj):
        return ", ".join([(v.voter.username, v.choice, v.show.title) for v in obj.votes.all()])

    list_display = ["name", "members_list", "shows_list", "votes_list"]


admin.site.register(Group, GroupAdmin)
