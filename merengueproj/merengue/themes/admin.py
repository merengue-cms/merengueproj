from merengue.base.admin import BaseAdmin, set_field_read_only
from themes.checker import check_themes
from themes.models import Theme


class ThemeAdmin(BaseAdmin):
    readonly_fields = ('name', 'description', 'directory_name', 'installed')
    list_display = ('name', 'directory_name', 'installed', 'active')

    def get_form(self, request, obj=None):
        form = super(ThemeAdmin, self).get_form(request, obj)
        if not obj.installed:
            set_field_read_only(form.base_fields['active'], 'active', obj)
        return form

    def changelist_view(self, request, extra_context=None):
        check_themes()
        return super(ThemeAdmin, self).changelist_view(request, extra_context)


def register(site):
    site.register(Theme, ThemeAdmin)
