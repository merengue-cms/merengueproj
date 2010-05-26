from django.utils.translation import ugettext as _

from merengue.block.blocks import Block
from plugins.highlight.models import Highlight


class HighlightBlock(Block):
    name = 'highlight'
    default_place = 'homepage'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        highlight_items = Highlight.objects.published()
        return cls.render_block(request, template_name='highlight/block_highlight.html',
                                block_title=_('Highlight'),
                                context={'highlight_items': highlight_items})
