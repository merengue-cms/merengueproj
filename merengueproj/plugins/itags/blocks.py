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
from plugins.itags.viewlets import TagCloudViewlet


class TagCloudBlock(Block):
    name = 'tagcloud'
    verbose_name = _('Tag cloud')
    help_text = _('Block with a tag cloud')
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        tag_cloud = TagCloudViewlet.get_tag_cloud(request)
        return cls.render_block(request, template_name='itags/blocks/tagcloud.html',
                                block_title=ugettext('Tag cloud'),
                                context={'taglist': tag_cloud})
