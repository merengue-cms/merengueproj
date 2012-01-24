import re

from django.conf import settings
from merengue.urlresolvers import get_url_default_lang


def treatment_middelware_microsite(url):
    if 'plugins.microsite.middleware.MicrositeMiddleware' in settings.MIDDLEWARE_CLASSES:
        from plugins.microsite.config import PluginConfig
        url_prefixes = PluginConfig.url_prefixes[0][0]
        prefix_microsite = url_prefixes.get(get_url_default_lang(),
                                                url_prefixes.get('en'))
        url = re.sub('^/%s' % prefix_microsite, '', url)
    return url
