from merengue.pluggable import Plugin

from plugins.facebook.actions import FacebookLink


class PluginConfig(Plugin):
    name = 'Facebook'
    description = 'Facebook integration plugin'
    version = '0.0.1a'
    url_prefixes = (
        #('news', 'plugins.facebook.urls'),
    )

    @classmethod
    def get_actions(cls):
        return [FacebookLink]
