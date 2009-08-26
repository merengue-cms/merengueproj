from merengue.plug import Plugin

from plugins.news.actions import PDFExport, NewsIndex
from plugins.news.blocks import LatestNewsBlock, NewsCommentsBlock


class PluginConfig(Plugin):
    name = 'News'
    description = 'News plugin'
    version = '0.0.1a'
    url_prefixes = (
        ('news', 'plugins.news.urls'),
    )
    media_dir = 'news'

    @classmethod
    def get_actions(cls):
        return [PDFExport, NewsIndex]

    @classmethod
    def get_blocks(cls):
        return [LatestNewsBlock, NewsCommentsBlock]
