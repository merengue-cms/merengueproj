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
from plugins.tv.models import VideoStreaming


class LatestVideoBlock(Block):
    name = 'latestVideo'
    default_place = 'rightsidebar'
    help_text = ugettext_lazy('Block provides latest videos')
    verbose_name = ugettext_lazy('Latest videos block')

    def render(self, request, channel, context, *args, **kwargs):
        video_list = VideoStreaming.objects.all()
        return self.render_block(request, template_name='tv/block_latest.html',
                                 block_title=_('Latest video'),
                                 context={'video_list': video_list})
