# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from merengue.block.blocks import Block


class AddThisBlock(Block):
    name = 'AddThisBlock'
    default_place = 'aftercontent'
    help_text = _('Block that displays AddThis links')
    verbose_name = _('AddThis service block')

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        from plugins.addthis.config import PluginConfig
        services = PluginConfig.get_config().get(
            'services', []).get_value()
        return cls.render_block(
            request, template_name='addthis/links_block.html',
            block_title=_('Share this'),
            context={'services': services},
            )
