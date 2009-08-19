from pluginregistry import Plugin

from plugins.news.actions import PDFExport


class PluginConfig(Plugin):
    name = 'News'
    description = 'News plugin'
    version = '0.0.1a'
    url_prefix = 'news'
    media_dir = 'news'

    @classmethod
    def get_actions(cls):
        return [PDFExport]
