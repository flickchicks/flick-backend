from django.contrib import admin

from .models import PrivateSuggestion


class PrivateSuggestionAdmin(admin.ModelAdmin):
    list_display = [
        "to_user",
        "from_user",
        "message",
        "show",
        "created_at",
        "updated_at",
    ]


admin.site.register(PrivateSuggestion, PrivateSuggestionAdmin)
