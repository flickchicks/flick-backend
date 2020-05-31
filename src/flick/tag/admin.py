from django.contrib import admin

from .models import Tag


# Register your models here.
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "tag"]


admin.site.register(Tag, TagAdmin)
