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

from merengue.block.blocks import Block, BaseBlock
from merengue.registry import params
from merengue.registry.items import BlockQuerySetItemProvider
from plugins.banner.params import BannerParam
from plugins.banner.views import get_banners


class BannerBlock(BlockQuerySetItemProvider, Block):
    name = 'banner'
    default_place = 'rightsidebar'
    verbose_name = _('Banner Block')
    help_text = _('Block that represents a list of banners')

    config_params = BaseBlock.config_params + BlockQuerySetItemProvider.config_params + [
        params.PositiveInteger(name='limit',
                               label=ugettext('limit for banner block'),
                               default=3),
        params.PositiveInteger(name='width',
                               label=ugettext('thumbnail maximum width'),
                               default=0),
        params.PositiveInteger(name='height',
                               label=ugettext('thumbnail maximum heigh'),
                               default=0),
    ]

    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def get_contents(self, request=None, context=None, section=None):
        banners_list = get_banners(request, filtering_section=False)
        return banners_list

    def render(self, request, place, context, *args, **kwargs):
        number_banners = self.get_config().get(
            'limit', []).get_value() or None
        width = self.get_config().get('width', []).get_value() or None
        height = self.get_config().get('height', []).get_value() or None
        size = None
        if width and height:
            size = str(width) + 'x' + str(height)
        elif width:
            size = str(width) + 'x' + str(width)
        elif height:
            size = str(height) + 'x' + str(height)
        banners = self.get_queryset(request, context)[:number_banners]
        return self.render_block(request,
                                 template_name='banner/block_banner.html',
                                 block_title=ugettext('banners'),
                                 context={'banners': banners,
                                          'size': size,
                                          })


class PortletBannerBlock(Block):
    name = 'portlet_banner'
    default_place = 'rightsidebar'
    verbose_name = _('Portlet Banner Block')
    help_text = _('Block that represents a banner')

    config_params = [
        params.PositiveInteger(name='width',
                               label=ugettext('thumbnail maximum width'),
                               default=0),
        params.PositiveInteger(name='height',
                               label=ugettext('thumbnail maximum heigh'),
                               default=0),
        BannerParam(name='banner',
                    label=ugettext('Choose a banner'),
                    default=None),
    ]

    def render(self, request, place, context, *args, **kwargs):
        width = self.get_config().get('width', []).get_value() or None
        height = self.get_config().get('height', []).get_value() or None
        size = None
        if width and height:
            size = str(width) + 'x' + str(height)
        elif width:
            size = str(width) + 'x' + str(width)
        elif height:
            size = str(height) + 'x' + str(height)
        banner_param = self.get_config().get('banner', None)
        if banner_param and banner_param.value:
            banner = banner_param.get_obj()
            block_title = unicode(banner)
        else:
            banner = None
            block_title = ugettext('Click in "configure block" and choose a banner')
        return self.render_block(request,
                                 template_name='banner/block_portlet_banner.html',
                                 block_title=block_title,
                                 context={'banner': banner,
                                          'size': size,
                                          })
