from django.contrib import admin
from plugins.custommeta.models import CustomMeta


class CustomMetaAdmin(admin.ModelAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(CustomMeta, CustomMetaAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(CustomMeta)
