from django.utils.translation import ugettext as _

from merengue.block.blocks import Block
from plugins.chunks.models import Chunk


class ChunksBlock(Block):
    name = 'chunksblock'
    default_place = 'all'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        chunks = Chunk.objects.placed_at(place, request.get_full_path())
        return cls.render_block(request, template_name='chunks/chunks_block.html',
                                block_title=_('Chunks'),
                                context={'chunks': chunks})
