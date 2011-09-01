# Copyright (c) 2011 by Yaco Sistemas
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
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import ContentAction
from plugins.forum.models import Forum
from plugins.forum.utils import can_create_new_thread


class CreateThreadAction(ContentAction):
    name = 'createthread'
    verbose_name = _(u'Create new thread')

    def get_response(self, request, content):
        http_response = can_create_new_thread(request, content)
        if http_response:
            return http_response
        else:
            return HttpResponseRedirect(reverse('plugins.forum.views.create_new_thread',
                                                kwargs={'forum_slug': content.slug}))

    def has_action(self, request, content):
        if request.user.is_anonymous():
            return False
        if type(content) == Forum:
            return content
        else:
            return None
