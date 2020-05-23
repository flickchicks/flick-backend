from django.contrib import admin
from .models import Asset, AssetBundle

from django.utils.safestring import mark_safe

# Register your models here.
class AssetBundleAdmin(admin.ModelAdmin):
    list_display = ['salt', 'kind']

admin.site.register(AssetBundle, AssetBundleAdmin)

class AssetAdmin(admin.ModelAdmin):
    def preview(self, obj):
        # use mark safe to show as image, not as html, in django admin
        return mark_safe(f'<img src="{obj.full_url}" width="100"/>')

    preview.allow_tags = True
    
    list_display = ['preview','kind', 'extension', 'full_url']

admin.site.register(Asset, AssetAdmin)

