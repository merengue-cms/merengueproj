from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import set_field_read_only
from merengue.plugins.checker import check_plugins
from merengue.plugins.models import RegisteredPlugin
from merengue.plugins.utils import has_required_dependencies
from merengue.registry.admin import RegisteredItemAdmin


class RegisteredPluginAdmin(RegisteredItemAdmin):
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name',
        'description', 'version', 'timestamp', 'directory_name')
    list_display = ('name', 'directory_name', 'installed', 'active',
                    'required_apps', 'required_plugins')

    def get_form(self, request, obj=None):
        form = super(RegisteredPluginAdmin, self).get_form(request, obj)
        if not obj.installed:
            set_field_read_only(form.base_fields['active'], 'active', obj)
        if not has_required_dependencies(obj):
            installed_field = form.base_fields['installed']
            help_text = installed_field.help_text
            installed_field.help_text = "%s %s" \
                                        % (help_text,
                                          _('Not all dependencies are met'))
            set_field_read_only(installed_field, 'installed', obj)
        return form

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        check_plugins()
        return super(RegisteredPluginAdmin, self).changelist_view(request,
            extra_context)


def register(site):
    site.register(RegisteredPlugin, RegisteredPluginAdmin)
