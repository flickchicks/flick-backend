from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Lst


# Register your models here.
class LstAdmin(admin.ModelAdmin):

    # show all assets in this bundle in django admin
    def preview(self, obj):
        html = ""
        for url in obj.poster_pics:
            # href makes image clickable to where it's being hosted
            html += f'<a href="{url}" target="_blank"><img src="{url}" width=90/></a>'

        return mark_safe(html)

    list_display = ["owner", "lst_name", "is_saved", "is_watch_later", "preview", "show_titles"]
    # readonly_fields = ('preview',)


admin.site.register(Lst, LstAdmin)
