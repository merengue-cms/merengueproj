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

from django.utils.translation import ugettext_lazy as _, ugettext

from merengue.registry import params
from merengue.registry.items import ViewLetQuerySetItemProvider
from merengue.viewlet.viewlets import Viewlet
from plugins.link.views import get_links


class LatestLinkViewlet(ViewLetQuerySetItemProvider, Viewlet):
    name = 'latestlink'
    help_text = _('Latest link')
    verbose_name = _('Latest links')

    config_params = ViewLetQuerySetItemProvider.config_params + [
        params.Single(
            name='limit',
            label=ugettext('limit for link viewlet'),
            default='10'),
    ]

    def get_contents(self, request=None, context=None, section=None):
        number_links = self.get_config().get('limit', []).get_value()
        link_list = get_links(request, number_links)
        return link_list

    def render(self, request, context):
        link_list = self.get_queryset(request, context)
        return self.render_viewlet(request, template_name='link/viewlet_latest.html',
                                  context={'link_list': link_list})


class AllLinkViewlet(ViewLetQuerySetItemProvider, Viewlet):
    name = 'alllink'
    help_text = _('All links')
    verbose_name = _('All links')

    def get_contents(self, request=None, context=None, section=None):
        link_list = get_links(request)
        return link_list

    def render(self, request, context):
        link_list = self.get_queryset(request, context)
        return self.render_viewlet(request, template_name='link/viewlet_latest.html',
                                  context={'link_list': link_list,
                                           'is_paginated': True,
                                           'paginate_by': 10})
