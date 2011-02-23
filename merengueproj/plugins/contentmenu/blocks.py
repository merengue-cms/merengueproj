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

from django.utils.translation import ugettext as _

from merengue.block.blocks import Block
from merengue.pluggable.utils import get_plugin

from plugins.contentmenu.models import ContentGroup


class ContentGroupLinksBlock(Block):
    name = 'contentgrouplinks'
    default_place = 'aftercontenttitle'

    def render(self, request, place, context, *args, **kwargs):
        content_groups = ContentGroup.objects.filter(contents=context['content'])
        if content_groups:
            filtered_contents = [[(child_cont.name, child_cont.public_link())
                                  for child_cont in cont.contents.all()]
                                 for cont in content_groups]
            numchars = get_plugin('contentmenu').get_config().get('numchars', []).get_value()
            return self.render_block(
                request, template_name='contentmenu/contentlinks_block.html',
                block_title=_('Content group links'),
                context={'contents': filtered_contents,
                         'numchars': numchars})
        else:
            return ''
