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

from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.block.blocks import Block
from merengue.registry import params
from merengue.registry.items import BlockQuerySetItemProvider
from plugins.news.views import get_news


class LatestNewsBlock(BlockQuerySetItemProvider, Block):
    name = 'latestnews'
    verbose_name = _('Latest news')
    help_text = _('Block with last news items published')
    default_place = 'leftsidebar'

    config_params = BlockQuerySetItemProvider.config_params + [
        params.PositiveInteger(
            name='limit',
            label=_('number of news for the "Latest news" block'),
            default=3,
        ),
    ]

    def get_contents(self, request=None, context=None, section=None):
        number_news = self.get_config().get('limit', []).get_value()
        news_list = get_news(request, number_news)
        return news_list

    def render(self, request, place, context, block_content_relation=None,
               *args, **kwargs):
        news_list = self.get_queryset(request, context)
        return self.render_block(request, template_name='news/block_latest.html',
                                 block_title=ugettext('Latest news'),
                                 context={'news_list': news_list})
