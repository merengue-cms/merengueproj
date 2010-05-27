from django.conf import settings
from django.core.cache import cache

from django.utils import translation


class ActivePluginsMiddleware(object):

    def process_request(self, request):
        if request.get_full_path().startswith(settings.MEDIA_URL):
            return None # plugin activation is not needed on static files
        from merengue.pluggable import PLUG_CACHE_KEY
        loaded = cache.get(PLUG_CACHE_KEY)
        if not loaded:
            from merengue.pluggable.utils import (enable_plugin,
                                                  get_plugin_module_name)
            from merengue.pluggable.models import RegisteredPlugin
            # enable active plugins
            active_plugins = RegisteredPlugin.objects.with_brokens().actives().cleaning_brokens()
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
            cache.set(PLUG_CACHE_KEY, 1)
        return None
