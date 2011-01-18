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

from merengue.block.blocks import Block
from merengue.registry.items import BlockQuerySetItemProvider

from plugins.event.utils import getEventsMonthYear
from plugins.event.views import get_events


class EventsCalendarBlock(BlockQuerySetItemProvider, Block):
    name = 'eventscalendar'
    default_place = 'rightsidebar'
    help_text = ugettext_lazy('Block that renders calendar with events')
    verbose_name = ugettext_lazy('Events Calendar Block')

    @classmethod
    def get_contents(cls, request=None, context=None, section=None):
        events = get_events(request)
        if not events.query.can_filter():
            events = events.model.objects.filter(id__in=events.values('id').query)

        return events

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        current_month = date.today().month
        current_year = date.today().year
        events = cls.get_queryset(request, context)
        events_dic = getEventsMonthYear(current_month, current_year, events)
        return cls.render_block(request,
                                template_name='event/block_calendar.html',
                                block_title=_('Events calendar'),
                                context={'events_dic': events_dic})
