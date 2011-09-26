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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ugettext_lazy

from merengue.block.blocks import Block
from merengue.pluggable.utils import get_plugin


class RSSGlobalFeed(Block):
    name = 'RSSGlobalFeed'
    default_place = 'meta'
    fixed_place = True
    is_addable = False
    help_text = ugettext_lazy('Block represents global RSS feed')
    verbose_name = ugettext_lazy('Global RSS feed block')

    default_caching_params = {
        'enabled': True,
        'timeout': 604800,
        'only_anonymous': False,
        'vary_on_user': False,
        'vary_on_url': False,
        'vary_on_language': False,
    }

    def render(self, request, place, context, *args, **kwargs):
        plugin = get_plugin("rss")
        portal_title = plugin.get_config().get('portal', '')
        feed_url = reverse('rss_views')
        return self.render_block(
            request, template_name='rss/global_block.html',
            block_title=_('RSS'),
            context={'feed_url': feed_url,
                     'portal_title': portal_title})
