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
from merengue.perms.utils import has_permission
from plugins.forum.models import Forum


class CreateThreadAction(ContentAction):
    name = 'createthread'
    verbose_name = _(u'Create new thread')

    def get_response(self, request, content):
        if request.user and (request.user.is_superuser or has_permission(content, request.user, 'create_new_thread')):
            return HttpResponseRedirect(reverse('plugins.forum.views.create_new_thread',
                                                kwargs={'forum_slug': content.slug}))
        else:
            login_url = '%s?next=%s' % (reverse('merengue_login'),
                                        request.get_full_path())
            return HttpResponseRedirect(login_url)

    def has_action(self, content):
        if type(content) == Forum:
            return content
        else:
            return None
