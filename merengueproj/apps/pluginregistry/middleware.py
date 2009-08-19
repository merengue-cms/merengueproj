from django.core.cache import cache

from pluginregistry.utils import enable_plugin, get_plugin_module_name
from pluginregistry.models import Plugin


class ActivePluginsMiddleware(object):

    def process_request(self, request):
        loaded = cache.get('pluginregistry__loaded')
        if not loaded:
            active_plugins = Plugin.objects.active()
            for plugin in active_plugins:
                plugin_name = get_plugin_module_name(plugin.directory_name)
                enable_plugin(plugin_name, register=False)
            cache.set('pluginregistry__loaded', 1)
        return None
