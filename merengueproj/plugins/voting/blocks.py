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

from merengue.block.blocks import ContentBlock
from merengue.registry import params
from merengue.registry.items import BlockConfigParamItemProvider

from plugins.voting.utils import get_can_vote


class VotingBlock(BlockConfigParamItemProvider, ContentBlock):
    name = 'voting'
    default_place = 'beforecontent'
    help_text = ugettext_lazy('Block that provides the voting functionality')
    verbose_name = ugettext_lazy('Voting block')

    config_params = BlockConfigParamItemProvider.config_params + [
        params.Bool(name='readonly', label=_('is readonly?'),
                    default=False),
    ]

    @classmethod
    def render(cls, request, place, content, context, *args, **kwargs):
        readonly = cls.get_config().get('readonly').get_value()
        return cls.render_block(request, template_name='voting/block_voting.html',
                                block_title=_('Vote content'),
                                context={'content': content,
                                         'can_vote': get_can_vote(content, request.user),
                                         'readonly': readonly,
                                         })
