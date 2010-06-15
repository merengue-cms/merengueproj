from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.news.actions import NewsIndex, NewsRSS
from plugins.news.blocks import LatestNewsBlock
from plugins.news.viewlets import LatestNewsViewlet, AllNewsViewlet

from plugins.news.models import NewsItem, NewsCategory
from plugins.news.admin import NewsItemSectionAdmin, NewsItemAdmin, NewsCategoryAdmin


class PluginConfig(Plugin):
    name = 'News'
    description = 'News plugin'
    version = '0.0.1a'

    config_params = [
        params.Single(name='limit', label=_('limit for templatetags'), default='3'),
    ]

    url_prefixes = (
        ('news', 'plugins.news.urls'),
    )

    @classmethod
    def get_actions(cls):
        return [NewsIndex, NewsRSS]

    @classmethod
    def get_blocks(cls):
        return [LatestNewsBlock]

    @classmethod
    def get_viewlets(cls):
        return [LatestNewsViewlet, AllNewsViewlet]

    @classmethod
    def section_models(cls):
        return [(NewsItem, NewsItemSectionAdmin)]

    @classmethod
    def get_model_admins(cls):
        return [(NewsCategory, NewsCategoryAdmin),
                (NewsItem, NewsItemAdmin)]
