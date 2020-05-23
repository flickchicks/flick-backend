from django.contrib import admin
from .models import Comment, Item, Like

# Register your models here.
class ItemAdmin(admin.ModelAdmin):
    list_display = ['owner', 'asset_bundle', 'created_at']

    search_fields = ['owner']

admin.site.register(Item, ItemAdmin)

class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Comment, CommentAdmin)

class LikeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Like, LikeAdmin)