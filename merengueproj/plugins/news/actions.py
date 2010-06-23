# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from merengue.action.actions import SiteAction


class NewsIndex(SiteAction):
    name = 'newsindex'
    verbose_name = _('News index')

    @classmethod
    def get_response(cls, request):
        return HttpResponseRedirect(reverse('news_index'))


class NewsRSS(SiteAction):
    name = 'newsrss'
    verbose_name = _('News rss')

    @classmethod
    def get_response(cls, request):
        return HttpResponseRedirect(reverse('news_index'))
