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
        while event_date.month == month and event_date <= event.end:
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
    return events_dic
