from merengue.pluggable import Plugin

from plugins.microsite.models import MicroSite
from plugins.microsite.admin import MicroSiteAdmin


class PluginConfig(Plugin):
    name = 'Micro Sites'
    description = 'Microsite plugin'
    version = '0.0.1a'

    url_prefixes = (
        ('microsite', 'plugins.microsite.urls'),
    )

    @classmethod
    def get_model_admins(cls):
        return [(MicroSite, MicroSiteAdmin)]
