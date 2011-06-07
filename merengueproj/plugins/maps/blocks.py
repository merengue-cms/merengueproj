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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _, get_language

from merengue.block.blocks import Block, BaseBlock
from merengue.registry import params


class MapBlock(Block):
    name = 'map'
    default_place = 'rightsidebar'
    help_text = _('Block that renders a google maps placed in a location')
    verbose_name = _('Maps Block')

    config_params = BaseBlock.config_params + [
        params.Float(
            name="latitude",
            label=_("map latitude"),
            default=37.390925,
        ),
        params.Float(
            name="longitude",
            label=_("map longitude"),
            default=-5.994844,
        ),
        params.Integer(
            name="width",
            label=_("Map width"),
            default=200,
        ),
        params.Integer(
            name="height",
            label=_("Map height"),
            default=200,
        ),
        params.Integer(
            name="zoom",
            label=_("Map zoom"),
            default=4,
        ),
        params.Bool(
            name="render_ui",
            label=_("Render UI"),
            default=True,
        ),
    ]

    def render(self, request, place, context, *args, **kwargs):
        context = {
            'zoom': self.get_config().get('zoom').get_value(),
            'latitude': self.get_config().get('latitude').get_value(),
            'longitude': self.get_config().get('longitude').get_value(),
            'width': self.get_config().get('width').get_value(),
            'height': self.get_config().get('height').get_value(),
            'render_ui': self.get_config().get('render_ui').get_value(),
            'MEDIA_URL': context.get('MEDIA_URL', settings.MEDIA_URL),
            'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
            'LANGUAGE_CODE': get_language(),
            'reg_block': self.reg_item,
            'request': context.get('request', None)}
        return self.render_block(
            request,
            template_name='maps/block_map.html',
            block_title=_('Map'),
            context=context,
        )
