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

import datetime

from django.core.urlresolvers import reverse
from django.db.models import Q

from plugins.event.models import Event


def getEventsMonthYear(month, year):
    filters = (
        Q(start__month=month, start__year=year) |
        Q(end__month=month, end__year=year),
    )
    events = Event.objects.all().filter(*filters)
    events_dic = {}
    for event in (i for i in events if i.is_published()):
        event_date = event.start
        while (event.start.month <= month <= event.end.month
            and event_date <= event.end):
            if event_date.month < month:
                event_date += datetime.timedelta(1)
                continue
            elif event_date.month > month:
                break

            key = "%s-%s-%s" % (event_date.year, event_date.month,
                                event_date.day)
            if key not in events_dic:
                events_dic[key] = {}
                events_dic[key]['name'] = []
                events_dic[key]['url'] = event.public_link()
            else:
                events_dic[key]['url'] = reverse("plugins.event.views.event_list",
                                            args=(event_date.year,
                                                  event_date.month,
                                                  event_date.day))

            events_dic[key]['name'].append(event.name)
            event_date += datetime.timedelta(1)
    for key in events_dic:
        html = '<br/>'.join('%s' % i for i in events_dic[key]['name'])
        events_dic[key]['name'] = html
    return events_dic
