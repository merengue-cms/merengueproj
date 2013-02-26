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

from datetime import date

from django.utils.translation import ugettext as _, ugettext_lazy

from merengue.block.blocks import Block, BaseBlock
from merengue.registry import params
from merengue.registry.items import BlockQuerySetItemProvider

from plugins.event.models import Event
from plugins.event.utils import getEventsMonthYear
from plugins.event.views import get_events


class EventsCalendarBlock(BlockQuerySetItemProvider, Block):
    name = 'eventscalendar'
    default_place = 'rightsidebar'
    help_text = ugettext_lazy('Block that renders calendar with events')
    verbose_name = ugettext_lazy('Events Calendar Block')
    cache_allowed = False

    @classmethod
    def get_models_refresh_cache(self):
        return [Event]

    def get_contents(self, request=None, context=None, section=None):
        return get_events(request, filtering_section=False)

    def render(self, request, place, context, *args, **kwargs):
        current_month = date.today().month
        current_year = date.today().year
        events = self.get_queryset(request, context)
        events_dic = getEventsMonthYear(current_month, current_year, events, True)
        section_id = 0
        section = self._get_section(request, context)
        if section and self.get_config().get('filtering_section', False).get_value():
            section_id = section.id
        return self.render_block(request,
                                 template_name='event/block_calendar.html',
                                 block_title=_('Events calendar'),
                                 context={'events_dic': events_dic,
                                          'section_id': section_id})


class LatestEventsBlock(BlockQuerySetItemProvider, Block):
    name = 'latestevents'
    verbose_name = _('Latest events')
    help_text = _('Block with last events items published')
    default_place = 'rightsidebar'

    config_params = BaseBlock.config_params + BlockQuerySetItemProvider.config_params + [
        params.PositiveInteger(
            name='limit',
            label=_('number of events for the "Latest events" block'),
            default=3,
        ),
    ]

    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    @classmethod
    def get_models_refresh_cache(self):
        return [Event]

    def get_contents(self, request=None, context=None, section=None):
        events_list = get_events(request, filtering_section=False)
        return events_list

    def render(self, request, place, context, *args, **kwargs):
        number_events = self.get_config().get('limit').get_value()
        events_list = self.get_queryset(request, context)[:number_events]
        if self.get_config().get('filtering_section', False) and not events_list:
            events_list = get_events(request, filtering_section=False)[:number_events]
        return self.render_block(request, template_name='event/block_latest.html',
                                 block_title=_('Latest events'),
                                 context={'events_list': events_list})
