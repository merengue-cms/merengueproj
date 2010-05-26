from merengue.pluggable import Plugin

from plugins.tv.blocks import LatestVideoBlock


class PluginConfig(Plugin):
    name = 'Tv'
    description = 'Tv plugin'
    version = '0.0.1a'

    url_prefixes = (
        ('canales-de-television', 'plugins.tv.urls'),
    )

    @classmethod
    def get_blocks(cls):
        return [LatestVideoBlock, ]
