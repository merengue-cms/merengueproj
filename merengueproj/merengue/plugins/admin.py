from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import set_field_read_only
from merengue.plug.checker import check_plugins
from merengue.plug.models import RegisteredPlugin
from merengue.plug.utils import get_plugin_config
from merengue.registry.admin import RegisteredItemAdmin


class RegisteredPluginAdmin(RegisteredItemAdmin):
    readonly_fields = RegisteredItemAdmin.readonly_fields + ('name',
        'description', 'version', 'timestamp', 'directory_name')
    list_display = ('name', 'directory_name', 'installed', 'active',
                    'requires_apps', 'requires_plugins')

    def get_form(self, request, obj=None):
        form = super(RegisteredPluginAdmin, self).get_form(request, obj)
        plugin_config = get_plugin_config(obj.directory_name)
        if not obj.installed:
            set_field_read_only(form.base_fields['active'], 'active', obj)
        # Check dependencies
        installed_field = form.base_fields['installed']
        plugin_config = get_plugin_config(obj.directory_name)
        required_apps = getattr(plugin_config, 'required_apps', ())
        required_apps_msg = u', '.join(required_apps)
        for app in required_apps:
            if app not in settings.INSTALLED_APPS:
                set_field_read_only(installed_field, 'installed', obj)
                installed_field.help_text += _(u'Requires applications: %s') \
                                             % required_apps_msg
            installed_field.help_text += '<br/>'
        required_plugins = getattr(plugin_config, 'required_plugins', ())
        required_plugins_msg = u', '.join(required_plugins)
        for plugin in required_plugins:
            if not RegisteredPlugin.objects.filter(directory_name=plugin,
                                                   active=True):
                set_field_read_only(installed_field, 'installed', obj)
                installed_field.help_text += _(u'Requires plugins: %s') \
                                             % required_plugins_msg
        return form

    def changelist_view(self, request, extra_context=None):
        check_plugins()
        return super(RegisteredPluginAdmin, self).changelist_view(request,
            extra_context)

    def requires_plugins(self, obj):
        plugin_config = get_plugin_config(obj.directory_name)
        required_plugins = getattr(plugin_config, 'required_plugins', ())
        return required_plugins or None
    requires_plugins.short_description = _('Requires plugins')

    def requires_apps(self, obj):
        plugin_config = get_plugin_config(obj.directory_name)
        required_apps = getattr(plugin_config, 'required_apps', ())
        return required_apps or None
    requires_apps.short_description = _('Requires applications')


def register(site):
    site.register(RegisteredPlugin, RegisteredPluginAdmin)
