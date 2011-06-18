# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

from django.utils.translation import ugettext_lazy

from merengue.block.blocks import Block


class PiwikBlock(Block):
    name = 'piwik'
    default_place = 'footer'
    help_text = ugettext_lazy('Block add piwik javascript')
    verbose_name = ugettext_lazy('Piwik Block')
    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': False,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': False,
    }

    def render(self, request, place, context, *args, **kwargs):
        content = context.get('content')
        section = context.get('section')
        return self.render_block(request, template_name='piwik/piwik_block.html',
                                 block_title='', context={'content': content,
                                                          'section': section})
