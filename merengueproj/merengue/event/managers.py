# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db.models import Q

from cmsutils.managers import ActiveManager

from base.managers import WorkflowManager, BaseContentManager


class EventManager(ActiveManager, BaseContentManager):
    """ don't show finished events
    """

    def __init__(self):
        super(EventManager, self).__init__(from_date='publish_date', to_date='expire_date')

    def actives(self):
        return super(EventManager, self).actives().filter(cached_max_end__gte=datetime.now(), status='published')

    def actives_in_date(self, onedate):
        return super(EventManager, self).actives().filter(cached_max_end__gte=onedate, status='published')

    def actives_in_range(self, start, end):
        return super(EventManager, self).actives().filter(Q(cached_max_end__lte=start, cached_max_end__gte=end), status='published')

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
        this_week_filter = Q(cached_min_start__lte=last_week_day,
                             cached_min_start__gte=first_week_day) | \
                           Q(cached_min_start__lte=day, cached_max_end__gte=day)
        return self.published().filter(this_week_filter)


class OccurrenceManager(WorkflowManager):
    """ don't show finished events
    """

    def by_status(self, status):
        return self.filter(event__status=status)

    def visibles(self):
        """ for use in views """
        return self.filter(end__gte=datetime.now()) or self.all()

    def published(self):
        """ only and visible published objects """
        return self.filter(event__status='published', end__gte=datetime.now())
