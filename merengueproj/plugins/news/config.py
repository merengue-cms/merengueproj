from merengue.plugins import Plugin

from plugins.news.actions import PDFExport, NewsIndex, NewsRSS
from plugins.news.blocks import LatestNewsBlock
from plugins.news.viewlets import LatestNewsViewlet

from plugins.news.models import NewsItem, NewsCategory
from plugins.news.admin import NewsItemSectionAdmin, NewsItemAdmin, NewsCategoryAdmin


class PluginConfig(Plugin):
    name = 'News'
    description = 'News plugin'
    version = '0.0.1a'
#    required_apps = ('django.contrib.flatpages', )
#    required_plugins = {
#        'event': {
#            'name': 'Events',
#            'version': '0.0.1a',
#        },
#    }
    url_prefixes = (
        ('news', 'plugins.news.urls'),
    )

    @classmethod
    def get_actions(cls):
        return [PDFExport, NewsIndex, NewsRSS]

    @classmethod
    def get_blocks(cls):
        return [LatestNewsBlock]

    @classmethod
    def get_viewlets(cls):
        return [LatestNewsViewlet, ]

    @classmethod
    def section_models(cls):
        return [(NewsItem, NewsItemSectionAdmin)]

    @classmethod
    def get_model_admins(cls):
        return [(NewsCategory, NewsCategoryAdmin),
                (NewsItem, NewsItemAdmin)]
