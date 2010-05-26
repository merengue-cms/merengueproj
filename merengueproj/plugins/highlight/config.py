from merengue.pluggable import Plugin

from plugins.highlight.blocks import HighlightBlock


class PluginConfig(Plugin):
    name = 'Highlight'
    description = 'Highlight content on home page'
    version = '0.0.1a'

    @classmethod
    def get_blocks(cls):
        return [HighlightBlock]
