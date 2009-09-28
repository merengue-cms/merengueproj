from django.conf import settings
from django.core.cache import cache

from django.utils import translation


class ActivePluginsMiddleware(object):

    def process_request(self, request):
        from merengue.plugins import PLUG_CACHE_KEY
        loaded = cache.get(PLUG_CACHE_KEY)
        if not loaded:
            from merengue.plugins.utils import (enable_plugin, disable_plugin,
                                             get_plugin_module_name)
            from merengue.plugins.models import RegisteredPlugin
            # enable active plugins
            active_plugins = RegisteredPlugin.objects.actives()
            plugin_names = [get_plugin_module_name(p.directory_name)
                            for p in active_plugins]
            for plugin_name in plugin_names:
                enable_plugin(plugin_name, register=True)
            # reset all i18n catalogs to load plugin ones
            if settings.USE_I18N:
                lang = translation.get_language()
                translation.trans_real._translations = {}
                translation.deactivate()
                translation.activate(lang)
            # deactivate inactive plugins
            inactive_plugins = RegisteredPlugin.objects.inactives()
            for plugin in inactive_plugins:
                plugin_name = get_plugin_module_name(plugin.directory_name)
                disable_plugin(plugin_name, unregister=True)
            cache.set(PLUG_CACHE_KEY, 1)
        return None
