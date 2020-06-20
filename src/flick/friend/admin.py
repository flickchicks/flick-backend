from django.contrib import admin
from friendship.models import FriendshipRequest, Friend

# Register your models here.


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "created", "rejected")


admin.site.unregister(FriendshipRequest)
admin.site.register(FriendshipRequest, FriendRequestAdmin)


class FriendAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "created")


admin.site.unregister(Friend)
admin.site.register(Friend, FriendAdmin)
