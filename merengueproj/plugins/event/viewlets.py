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
from plugins.event.views import get_events


class LatestEventViewlet(ViewLetQuerySetItemProvider, Viewlet):
    name = 'latestevents'
    help_text = _('Latest events')
    verbose_name = _('Latest Event')

    config_params = ViewLetQuerySetItemProvider.config_params + [
        params.Single(
            name='limit',
            label=ugettext('limit for event viewlet'),
            default='10'),
    ]

    def get_contents(self, request=None, context=None, section=None):
        number_events = self.get_config().get('limit', []).get_value()
        event_list = get_events(request, number_events)
        return event_list

    def render(self, request, context):
        event_list = self.get_queryset(request, context)
        return self.render_viewlet(request, template_name='event/viewlet_latest.html',
                                  context={'event_list': event_list})


class AllEventViewlet(ViewLetQuerySetItemProvider, Viewlet):
    name = 'allevent'
    help_text = _('All events')
    verbose_name = _('All events')

    config_params = ViewLetQuerySetItemProvider.config_params + [
        params.Single(
            name='page_elements',
            label=ugettext('number of elements on a page'),
            default='10'),
    ]

    def get_contents(self, request=None, context=None, section=None):
        event_list = get_events(request)
        return event_list

    def render(self, request, context):
        per_page = self.get_config().get('page_elements', []).get_value()
        event_list = self.get_queryset(request, context)
        return self.render_viewlet(request, template_name='event/viewlet_latest.html',
                                  context={'event_list': event_list,
                                           'is_paginated': True,
                                           'paginate_by': int(per_page)})
