from django.utils.translation import ugettext as _

from merengue.block.blocks import ContentBlock


class CoreMenuBlock(ContentBlock):
    name = 'coremenu'
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request, content):
        sections = content.basesection_set.all()
        section = None
        if sections:
            section = sections[0].real_instance

        return cls.render_block(request, template_name='core/block_menu.html',
                                block_title=_('Menu'),
                                context={'section': section})
