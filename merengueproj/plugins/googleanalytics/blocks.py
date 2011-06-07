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

from merengue.block.blocks import Block, BaseBlock
from merengue.registry import params


class GoogleAnalyticsBlock(Block):
    name = 'map'
    default_place = 'meta'
    help_text = _('Block that includes the javascript needed to enable google analytics')
    verbose_name = _('Google Analytics Block')

    config_params = BaseBlock.config_params + [
        params.Single(
            name="google_analytics_id",
            label=_("google analytics id"),
            default='',
        ),
        params.Single(
            name="web_master_tools_id",
            label=_("Web master tools id"),
            default='',
        ),
    ]

    def render(self, request, place, context, *args, **kwargs):
        context = {
            'google_analytics_id': self.get_config().get('google_analytics_id').get_value(),
            'web_master_tools_id': self.get_config().get('web_master_tools_id').get_value(),
            }
        return self.render_block(
            request,
            template_name='googleanalytics/googleanalytics_block.html',
            block_title=_('Google Analytics'),
            context=context,
        )
