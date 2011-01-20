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

# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db.models import Q

from cmsutils.managers import ActiveManager

from merengue.base.managers import BaseContentManager


class EventManager(ActiveManager, BaseContentManager):
    """ don't show finished events
    """

    def __init__(self):
        super(EventManager, self).__init__(from_date='publish_date', to_date='expire_date')

    def actives(self):
        return super(EventManager, self).actives().filter(end__gte=datetime.now())

    def actives_in_date(self, onedate):
        return super(EventManager, self).actives().filter(end__gte=onedate)

    def actives_in_range(self, start, end):
        return super(EventManager, self).actives().filter(Q(end__lte=start, end__gte=end))

    def allpublished(self):
        return self.filter(status='published')

    def published(self):
        return self.actives().filter(status='published')

    def by_week(self, day):
        """ weekly events from a day in a week, passed by param. Events returned will be:
             a) events with initial date in same week that day, or
             b) events with day between initial and end date """
        weekday = day.weekday()
        first_week_day = datetime(day.year, day.month, day.day, hour=0, minute=0) - timedelta(weekday)
        last_week_day = datetime(day.year, day.month, day.day, hour=23, minute=59) + timedelta(6-weekday)
        this_week_filter = Q(start__lte=last_week_day,
                             start__gte=first_week_day) | \
                           Q(start__lte=day, end__gte=day)
        return self.published().filter(this_week_filter)
