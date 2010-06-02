from django.conf import settings
from django.utils import translation

from merengue.pluggable.loading import load_plugins, plugins_loaded


class ActivePluginsMiddleware(object):

    def process_request(self, request):
        if request.get_full_path().startswith(settings.MEDIA_URL):
            return None # plugin activation is not needed on static files
        if not plugins_loaded():
            load_plugins()
            # reset all i18n catalogs to load plugin ones
            if settings.USE_I18N:
                lang = translation.get_language()
                translation.trans_real._translations = {}
                translation.deactivate()
                translation.activate(lang)
        return None
