from base.admin import BaseAdmin, set_field_read_only
from pluginregistry.checker import check_plugins
from pluginregistry.models import Plugin


class PluginAdmin(BaseAdmin):
    readonly_fields = ('name', 'description', 'version', 'timestamp', 'directory_name')
    list_display = ('name', 'directory_name', 'installed', 'active')

    def get_form(self, request, obj=None):
        form = super(PluginAdmin, self).get_form(request, obj)
        if not obj.installed:
            set_field_read_only(form.base_fields['active'], 'active', obj)
        return form

    def changelist_view(self, request, extra_context=None):
        check_plugins()
        return super(PluginAdmin, self).changelist_view(request, extra_context)


def register(site):
    site.register(Plugin, PluginAdmin)
