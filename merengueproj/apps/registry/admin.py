from base.admin import BaseAdmin
from registry.models import RegisteredItem


class RegisteredItemAdmin(BaseAdmin):
    readonly_fields = ('class_name', 'module', 'category', )
    list_display = ('class_name', 'module', 'category', )
    list_filter = ('category', )


def register(site):
    site.register(RegisteredItem, RegisteredItemAdmin)
