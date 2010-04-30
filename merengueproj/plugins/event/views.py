from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.simplejson import dumps

from merengue.base.views import content_view

from plugins.event.models import Event
from plugins.event.utils import getEventsMonthYear


def event_view(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    return content_view(request, event, 'event/event_view.html')


def events_calendar(request):
    mimetype = "application/json"
    if (request.GET and request.is_ajax() and 'month' in request.GET
        and 'year' in request.GET):
        month = int(request.GET['month'])
        year = int(request.GET['year'])
        events_dic = getEventsMonthYear(month, year)
        return HttpResponse(dumps(events_dic), mimetype=mimetype)
    return HttpResponseBadRequest(mimetype=mimetype)
