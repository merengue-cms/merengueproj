from pluginregistry import add_to_installed_apps, get_plugin_module_name
from pluginregistry.models import Plugin


class ActivePluginsMiddleware(object):

    def process_request(self, request):
        active_plugins = Plugin.objects.active()
        for plugin in active_plugins:
            plugin_name = get_plugin_module_name(plugin.directory_name)
            add_to_installed_apps(plugin_name)
        return None
