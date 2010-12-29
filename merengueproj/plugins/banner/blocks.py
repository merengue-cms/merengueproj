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

from django.utils.translation import ugettext as _, ugettext_lazy

from merengue.block.blocks import Block
from plugins.banner.views import get_banners


class BannerBlock(Block):
    name = 'banner'
    default_place = 'rightsidebar'
    verbose_name = ugettext_lazy('Banner Block')
    help_text = ugettext_lazy('Block that represents a banner')

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        from plugins.banner.config import PluginConfig
        limit = PluginConfig.get_config().get('limit', None)
        limit = limit and limit.get_value()
        banners = get_banners(request, limit)
        return cls.render_block(request, template_name='banner/block_banner.html',
                                block_title=_('banners'),
                                context={'banners': banners})
