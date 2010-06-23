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

from datetime import date

from django.utils.translation import ugettext as _

from merengue.block.blocks import Block

from plugins.event.utils import getEventsMonthYear


class EventsCalendarBlock(Block):
    name = 'eventscalendar'
    default_place = 'rightsidebar'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        current_month = date.today().month
        current_year = date.today().year
        events_dic = getEventsMonthYear(current_month, current_year)
        return cls.render_block(request,
                                template_name='event/block_calendar.html',
                                block_title=_('Events calendar'),
                                context={'events_dic': events_dic})
