from base.admin import BaseAdmin
from registry.models import RegistedItem


class RegistedItemAdmin(BaseAdmin):
    readonly_fields = ('class_name', 'module', )
    list_display = ('class_name', 'module', )


def register(site):
    site.register(RegistedItem, RegistedItemAdmin)
