from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Show


# Register your models here.
class ShowAdmin(admin.ModelAdmin):
    # show all assets in this bundle in django admin
    def preview(self, obj):
        html = f'<a href="{obj.poster_pic}" target="_blank"><img src="{obj.poster_pic}" width=128/></a>'
        return mark_safe(html)

    list_display = ["id", "preview", "title", "directors", "date_released", "ext_api_source"]


admin.site.register(Show, ShowAdmin)
