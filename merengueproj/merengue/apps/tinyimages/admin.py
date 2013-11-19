from django.contrib import admin

from tinyimages.models import TinyImage, TinyFile


class TinyImageAdmin(admin.ModelAdmin):
    """ Admin options for tinyimage """
    list_display = ('title', )


class TinyFileAdmin(admin.ModelAdmin):
    """ Admin options for tinyimage """
    list_display = ('title', )


admin.site.register(TinyFile, TinyFileAdmin)
admin.site.register(TinyImage, TinyImageAdmin)
