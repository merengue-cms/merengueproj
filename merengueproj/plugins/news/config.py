from merengue.plugins import Plugin

from plugins.news.actions import PDFExport, NewsIndex, NewsRSS
from plugins.news.blocks import LatestNewsBlock, NewsCommentsBlock

from plugins.news.models import NewsItem
from plugins.news.admin import NewsItemSectionAdmin


class PluginConfig(Plugin):
    name = 'News'
    description = 'News plugin'
    version = '0.0.1a'
    # required_apps = ('django.contrib.flatpages', )
    # required_plugins = ('event', )
    url_prefixes = (
        ('news', 'plugins.news.urls'),
    )

    @classmethod
    def get_actions(cls):
        return [PDFExport, NewsIndex, NewsRSS]

    @classmethod
    def get_blocks(cls):
        return [LatestNewsBlock, NewsCommentsBlock]

    @classmethod
    def section_models(cls):
        return [(NewsItem, NewsItemSectionAdmin)]
