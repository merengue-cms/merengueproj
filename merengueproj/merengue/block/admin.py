from merengue.registry.admin import RegisteredItemAdmin
from merengue.block.models import RegisteredBlock


class RegisteredBlockAdmin(RegisteredItemAdmin):
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name', )
    list_display = RegisteredItemAdmin.list_display + ('placed_at', )
    list_filter = ('placed_at', )


def register(site):
    site.register(RegisteredBlock, RegisteredBlockAdmin)
