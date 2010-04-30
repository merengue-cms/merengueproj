from django.db.models import Q

from plugins.event.models import Event


def getEventsMonthYear(month, year):
    filters = (
        Q(start__month=month, start__year=year) |
        Q(end__month=month, end__year=year),
    )
    events = Event.objects.all().filter(*filters)
    events_dic = {}
    for event in events:
        key = "%s-%s-%s" % (event.start.year, event.start.month,
                            event.start.day)
        if key not in events_dic:
            events_dic[key] = {}
            events_dic[key]['name'] = []
        events_dic[key]['name'].append(event.name)
        events_dic[key]['url'] = event.public_link()
    return events_dic
