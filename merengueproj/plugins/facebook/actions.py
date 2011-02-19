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

from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import ContentAction


class FacebookLink(ContentAction):
    name = 'facebooklink'
    verbose_name = _('Share in Facebook')
    help_text = _('Facebook share widget')

    def get_response(self, request, content):
        request_url = 'http://%s%s' % (Site.objects.get_current().domain, content.public_link())
        return HttpResponseRedirect('http://www.facebook.com/share.php?u=%s' % urlquote(request_url))
