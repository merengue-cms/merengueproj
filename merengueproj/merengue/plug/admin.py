from merengue.base.admin import set_field_read_only
from merengue.plug.checker import check_plugins
from merengue.plug.models import RegisteredPlugin
from merengue.registry.admin import RegisteredItemAdmin


class RegisteredPluginAdmin(RegisteredItemAdmin):
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name', 'description', 'version', 'timestamp', 'directory_name')
    list_display = ('name', 'directory_name', 'installed', 'active')

    def get_form(self, request, obj=None):
        form = super(RegisteredPluginAdmin, self).get_form(request, obj)
        if not obj.installed:
            set_field_read_only(form.base_fields['active'], 'active', obj)
        return form

    def changelist_view(self, request, extra_context=None):
        check_plugins()
        return super(RegisteredPluginAdmin, self).changelist_view(request, extra_context)


def register(site):
    site.register(RegisteredPlugin, RegisteredPluginAdmin)
