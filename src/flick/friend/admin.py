from django.contrib import admin

from friendship.models import FriendshipRequest, Friend


class FriendRequestAdmin(admin.ModelAdmin):
    """
    override registered modal Friend Request from django-friendship
    """

    list_display = ("from_user", "to_user", "created", "rejected")


admin.site.unregister(FriendshipRequest)
admin.site.register(FriendshipRequest, FriendRequestAdmin)


class FriendAdmin(admin.ModelAdmin):
    """
    override registered modal Friend from django-friendship
    """

    list_display = ("from_user", "to_user", "created")


admin.site.unregister(Friend)
admin.site.register(Friend, FriendAdmin)
