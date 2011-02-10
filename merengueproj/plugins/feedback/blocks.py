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


class FeedbackBlock(ContentBlock):
    name = 'feedback'
    default_place = 'aftercontent'
    verbose_name = ugettext_lazy('Feedback block')
    help_text = ugettext_lazy('The block represents the feedback widget')

    def render(self, request, place, content, context, *args, **kwargs):
        if content.is_commentable():
            return self.render_block(request, template_name='feedback/block_feedback.html',
                                     block_title=_('Feedback content'),
                                     context={'content': content})
        return ''
