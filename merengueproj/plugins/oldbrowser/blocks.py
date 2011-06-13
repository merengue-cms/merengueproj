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

import re

from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _

from merengue.block.blocks import Block
from plugins.oldbrowser.models import OldBrowser


class OldBrowserBlock(Block):
    name = 'oldbrowser'
    default_place = 'header'
    help_text = _('Block emulates the old browser ')
    verbose_name = _('Old browser block')
    cache_allowed = False

    def render(self, request, place, context, *args, **kwargs):
        user_agent = request.META.get('HTTP_USER_AGENT', None)
        if not user_agent:
            return ''
        warning_string = None
        for oldbrowser in OldBrowser.objects.all():
            if re.search(oldbrowser.user_agent, user_agent, flags=re.I):
                warning_string = _(u'Your browser is too old. Please, update it.')
                if settings.DEBUG:
                    warning_string = u'(%s) %s' % (oldbrowser.user_agent,
                                                   warning_string)
        return self.render_block(request, template_name='oldbrowser/block_oldbrowser.html',
                                 block_title=ugettext('Old Browser'), context={'warning_string': warning_string})
