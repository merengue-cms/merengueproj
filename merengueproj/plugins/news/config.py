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
        params.PositiveInteger(
            name='limit',
            label=_('number of news for the "Latest news" block'),
            default=3,
        ),
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
