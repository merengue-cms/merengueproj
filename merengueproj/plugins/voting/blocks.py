from django.utils.translation import ugettext as _

from merengue.block.blocks import ContentBlock


class VotingBlock(ContentBlock):
    name = 'voting'
    default_place = 'beforecontent'

    @classmethod
    def render(cls, request, place, content):
        return cls.render_block(request, template_name='voting/block_voting.html',
                                block_title=_('Vote content'),
                                context={'content': content})
