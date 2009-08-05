from base.admin import BaseAdmin
from themes.checker import check_themes
from themes.models import Theme


class ThemeAdmin(BaseAdmin):
    readonly_fields = ('name', 'description', 'directory_name')
    list_display = ('name', 'directory_name', 'enabled', 'active')

    def changelist_view(self, request, extra_context=None):
        check_themes()
        return super(ThemeAdmin, self).changelist_view(request, extra_context)


def register(site):
    site.register(Theme, ThemeAdmin)
