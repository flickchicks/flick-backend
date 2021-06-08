from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Asset
from .models import AssetBundle


class AssetBundleAdmin(admin.ModelAdmin):

    # show all assets in this bundle in django admin
    def preview(self, obj):
        html = "<ul>"
        for url in obj.asset_urls.values():
            # href makes image clickable to where it's being hosted
            html += f'<li><a href="{url}" target="_blank"><img src="{url}" width=128/></a></li>'
        html += "</ul>"
        return mark_safe(html)

    list_display = ["salt"]
    readonly_fields = ("preview",)


admin.site.register(AssetBundle, AssetBundleAdmin)


class AssetAdmin(admin.ModelAdmin):

    # use mark safe to show as image, not as html, in django admin
    def preview(self, obj):
        return mark_safe(f'<img src="{obj.full_url}" width="100"/>')

    preview.allow_tags = True

    list_display = ["preview", "extension", "full_url"]


admin.site.register(Asset, AssetAdmin)
