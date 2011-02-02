# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from merengue.collection.utils import create_normalize_collection
from merengue.pluggable import Plugin

from plugins.news.actions import NewsIndex, NewsRSS
from plugins.news.blocks import LatestNewsBlock
from plugins.news.viewlets import LatestNewsViewlet, AllNewsViewlet

from plugins.news.models import NewsItem, NewsCategory
from plugins.news.admin import NewsItemSectionAdmin, NewsItemAdmin, NewsCategoryAdmin


class PluginConfig(Plugin):
    name = 'News'
    description = 'News plugin'
    version = '0.0.1a'

    url_prefixes = (
        ({'en': 'news', 'es': 'noticias'}, 'plugins.news.urls'),
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

    @classmethod
    def post_install(cls):
        create_normalize_collection('news', u'News', NewsItem,
                                    create_display_field=True,
                                    create_filter_field=True)
