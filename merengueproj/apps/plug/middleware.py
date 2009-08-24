from django.core.cache import cache

from plug.utils import enable_plugin, get_plugin_module_name
from plug.models import RegisteredPlugin


class ActivePluginsMiddleware(object):

    def process_request(self, request):
        loaded = cache.get('plug__loaded')
        if not loaded:
            active_plugins = RegisteredPlugin.objects.actives()
            for plugin in active_plugins:
                plugin_name = get_plugin_module_name(plugin.directory_name)
                enable_plugin(plugin_name, register=False)
            cache.set('plug__loaded', 1)
        return None
