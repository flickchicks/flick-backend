from django.contrib import admin
from api.models import Item

# Register your models here.
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'like_count', 'full_title', 'owner', 'owner_email']

    search_fields = ['title']

admin.site.register(Item, ItemAdmin)
