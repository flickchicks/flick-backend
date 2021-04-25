from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "bio",
        "profile_pic",
        "phone_number",
        "social_id",
        "social_id_token_type",
        "notif_time_viewed",
        "suggest_time_viewed",
    ]


admin.site.register(Profile, ProfileAdmin)
