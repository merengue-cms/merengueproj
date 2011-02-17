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

from django.utils.translation import ugettext_lazy as _, ugettext

from merengue.block.blocks import Block
from merengue.registry import params
from merengue.registry.items import BlockQuerySetItemProvider
from plugins.banner.views import get_banners


class BannerBlock(BlockQuerySetItemProvider, Block):
    name = 'banner'
    default_place = 'rightsidebar'
    verbose_name = _('Banner Block')
    help_text = _('Block that represents a banner')

    config_params = BlockQuerySetItemProvider.config_params + [
        params.Single(name='limit', label=ugettext('limit for banner block'),
                      default='3'),
    ]

    def get_contents(self, request=None, context=None, section=None):
        banners_list = get_banners(request, filtering_section=False)
        return banners_list

    def render(self, request, place, context, *args, **kwargs):
        number_banners = self.get_config().get(
            'limit', []).get_value() or None
        banners = self.get_queryset(request, context)[:number_banners]
        return self.render_block(request, template_name='banner/block_banner.html',
                                 block_title=ugettext('banners'),
                                 context={'banners': banners})
