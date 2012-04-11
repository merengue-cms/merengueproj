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
from merengue.section.utils import get_section
from plugins.microsite.models import MicroSiteLink, MicroSite


class HighlightMenu(Block):
    name = 'highlightmenu'
    verbose_name = _('Highlight menu')
    help_text = _('Block with the microsite links')
    default_place = 'rightsidebar'

    config_params = Block.config_params + BlockQuerySetItemProvider.config_params + [
        params.PositiveInteger(
            name='limit',
            label=_('number of links for the "Highlight menu" block'),
            default=5,
        ),
        params.Single(
            name='background',
            label=_('background color for the "Highlight menu" block'),
            default='#ffffff',
        ),
        params.Single(
            name='link_color',
            label=_('color of the links inside the "Highlight menu" block'),
            default='#0000ff',
        ),
        params.Single(
            name='over_color',
            label=_('color of the links (when the mouse is over) inside the "Highlight menu" block'),
            default='#ff00ff',
        ),
    ]

    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    @classmethod
    def get_models_refresh_cache(self):
        return [MicroSiteLink]

    def render(self, request, place, context, *args, **kwargs):
        section = get_section(request, context)
        if isinstance(section, MicroSite):
            microsite = section
            limit = self.get_config().get('limit').get_value()
            links = MicroSiteLink.objects.filter(microsite=microsite).visible_by_user(request.user)
            links = links[:limit]
            conf = {
                'background': self.get_config().get('background').get_value(),
                'link_color': self.get_config().get('link_color').get_value(),
                'over_color': self.get_config().get('over_color').get_value(),
            }
        else:
            microsite = None
            links = []
            conf = {}
        return self.render_block(request, template_name='microsite/blocks/highlight_menu.html',
                                 block_title=ugettext('Highlight menu'),
                                 context={'microsite': microsite,
                                          'links': links,
                                          'conf': conf})
