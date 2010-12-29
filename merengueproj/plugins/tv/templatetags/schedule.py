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

# Template tag
import datetime

from django import template
from django.utils.dates import MONTHS

register = template.Library()


def get_last_day_of_month(year, month):
    if (month == 12):
        year += 1
        month = 1
    else:
        month += 1
    return datetime.date(year, month, 1) - datetime.timedelta(1)


def month_cal(month, year):
    first_day_of_month = datetime.date(year, month, 1)
    last_day_of_month = get_last_day_of_month(year, month)
    first_day_of_calendar = (first_day_of_month -
                             datetime.timedelta(first_day_of_month.weekday()))
    last_day_of_calendar = last_day_of_month + datetime.timedelta(7 -
                            last_day_of_month.weekday())

    month_cal = []
    week = []
    week_headers = []
    weekends = 5
    i = 0
    day = first_day_of_calendar
    while day <= last_day_of_calendar:
        if i < 7:
            week_headers.append(day)
        cal_day = {}
        cal_day['day'] = day
        if day.month == month:
            cal_day['in_month'] = True
        else:
            cal_day['in_month'] = False
        if i in [weekends, weekends+1]:
            cal_day['weekend'] = True
        if i == weekends +1:
            weekends +=7
        week.append(cal_day)

        if day.weekday() == 6:
            month_cal.append(week)
            week = []
        i += 1
        day += datetime.timedelta(days=1)

    return {'year': year,
            'month': MONTHS[month],
            'month_number': month,
            'calendar': month_cal,
            'headers': week_headers}

register.inclusion_tag('tv/calendar.html')(month_cal)


def get_week_view_params(date):
    init_week = date - datetime.timedelta(date.weekday())
    return 'broadcast_date__gte=%s' % init_week.toordinal()
register.simple_tag(get_week_view_params)
