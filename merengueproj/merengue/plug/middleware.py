from django.core.cache import cache


class ActivePluginsMiddleware(object):

    def process_request(self, request):
        from merengue.plug import PLUG_CACHE_KEY
        loaded = cache.get(PLUG_CACHE_KEY)
        if not loaded:
            from merengue.plug.utils import enable_plugin, disable_plugin, get_plugin_module_name
            from merengue.plug.models import RegisteredPlugin
            active_plugins = RegisteredPlugin.objects.actives()
            for plugin in active_plugins:
                plugin_name = get_plugin_module_name(plugin.directory_name)
                enable_plugin(plugin_name, register=True)
            inactive_plugins = RegisteredPlugin.objects.inactives()
            for plugin in inactive_plugins:
                plugin_name = get_plugin_module_name(plugin.directory_name)
                disable_plugin(plugin_name, unregister=True)
            cache.set(PLUG_CACHE_KEY, 1)
        return None
