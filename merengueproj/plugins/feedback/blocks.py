from django.utils.translation import ugettext as _

from merengue.block.blocks import ContentBlock


class FeedbackBlock(ContentBlock):
    name = 'feedback'
    default_place = 'aftercontent'

    @classmethod
    def render(cls, request, place, content, context, *args, **kwargs):
        if content.is_commentable():
            return cls.render_block(request, template_name='feedback/block_feedback.html',
                                    block_title=_('Feedback content'),
                                    context={'content': content})
        return ''
