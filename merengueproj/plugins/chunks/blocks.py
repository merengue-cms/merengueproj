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
from plugins.chunks.models import Chunk


class ChunksBlock(Block):
    name = 'chunksblock'
    default_place = 'all'
    help_text = ugettext_lazy('Chunks Block')
    verbose_name = ugettext_lazy('Chunks Block')

    def render(self, request, place, context, *args, **kwargs):
        chunks = Chunk.objects.placed_at(place, request.get_full_path())
        return self.render_block(request, template_name='chunks/chunks_block.html',
                                 block_title=_('Chunks'),
                                 context={'chunks': chunks})
