from django.utils.translation import ugettext as _

from merengue.block.blocks import Block


class CoreMenuBlock(Block):
    name = 'coremenu'
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request):
        if not request.section:
            return '' # renders nothing
        return cls.render_block(request, template_name='core/block_menu.html',
                                block_title=_('Menu'),
                                context={'section': request.section})
