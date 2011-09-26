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

from django.core.urlresolvers import reverse

from plugins.event.managers import get_first_day_of_month, get_last_day_of_month


def getEventsMonthYear(month, year, events):
    events = events.model.objects.by_month(month=month, year=year).filter(id__in=events.values('id').query)
    start_date = get_first_day_of_month(month, year)
    end_date = get_last_day_of_month(month, year)
    events_dic = {}
    for event in events:
        days = event.get_days_actives(start_date, end_date)
        event_url = event.get_absolute_url()
        for day in days:
            key = "%s-%s-%s" % (day.year, day.month,
                                day.day)
            if key not in events_dic:
                events_dic[key] = {}
                events_dic[key]['name'] = event.name
                events_dic[key]['url'] = event_url
            else:
                events_dic[key]['name'] += '<br/> %s' % event.name
                events_dic[key]['url'] = reverse("plugins.event.views.event_list",
                                                  args=(day.year,
                                                        day.month,
                                                        day.day))
    return events_dic
