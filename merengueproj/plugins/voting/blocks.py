from django.utils.translation import ugettext as _

from merengue.block.blocks import ContentBlock

from plugins.voting.utils import get_can_vote


class VotingBlock(ContentBlock):
    name = 'voting'
    default_place = 'beforecontent'

    @classmethod
    def render(cls, request, place, content, context, *args, **kwargs):
        from plugins.voting.config import PluginConfig
        plugin_config = PluginConfig.get_config()
        readonly = plugin_config.get('readonly').get_value() != u'False'
        return cls.render_block(request, template_name='voting/block_voting.html',
                                block_title=_('Vote content'),
                                context={'content': content,
                                         'can_vote': get_can_vote(content, request.user),
                                         'readonly': readonly,
                                         })
