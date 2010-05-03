import datetime

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.simplejson import dumps

from merengue.base.views import content_view, content_list

from plugins.event.models import Event
from plugins.event.utils import getEventsMonthYear


def event_view(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    return content_view(request, event, 'event/event_view.html')


def event_list(request, year, month, day):
    date_day_start = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
    date_day_end = datetime.datetime(int(year), int(month), int(day), 23, 59, 59)
    events = Event.objects.filter(start__lt=date_day_end).filter(end__gt=date_day_start)
    return content_list(request, events,
                        extra_context={'date': date_day_start},
                        template_name='event/event_list.html')


def events_calendar(request):
    mimetype = "application/json"
    if (request.GET and 'month' in request.GET
        and 'year' in request.GET):
        month = int(request.GET['month'])
        year = int(request.GET['year'])
        events_dic = getEventsMonthYear(month, year)
        return HttpResponse(dumps(events_dic), mimetype=mimetype)
    return HttpResponseBadRequest(mimetype=mimetype)
