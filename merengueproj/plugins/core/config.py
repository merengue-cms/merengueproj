from merengue.plugins import Plugin

from plugins.core.blocks import CoreMenuBlock


class PluginConfig(Plugin):
    name = 'Core'
    description = 'Core plugin'
    version = '0.0.1a'

    url_prefixes = (
    )

    @classmethod
    def get_blocks(cls):
        return [CoreMenuBlock]
