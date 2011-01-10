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

from django.utils.translation import ugettext_lazy as _

from merengue.viewlet.viewlets import Viewlet
from plugins.link.views import get_links


class LatestLinkViewlet(Viewlet):
    name = 'latestlink'
    help_text = _('Latest link')
    verbose_name = _('Latest links')

    @classmethod
    def render(cls, request):
        link_list = get_links(request, 10)
        return cls.render_viewlet(request, template_name='link/viewlet_latest.html',
                                  context={'link_list': link_list})


class AllLinkViewlet(Viewlet):
    name = 'alllink'
    help_text = _('All links')
    verbose_name = _('All links')

    @classmethod
    def render(cls, request):
        link_list = get_links(request)
        return cls.render_viewlet(request, template_name='link/viewlet_latest.html',
                                  context={'link_list': link_list,
                                           'is_paginated': True,
                                           'paginate_by': 10})
