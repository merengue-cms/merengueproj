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

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.simplejson import dumps

from merengue.base.views import content_view, content_list

from cmsutils.adminfilters import QueryStringManager

from plugins.event.models import Event, Category
from plugins.event.utils import getEventsMonthYear


def event_view(request, event_slug, extra_context=None):
    event = get_object_or_404(Event, slug=event_slug)
    event_category_slug = request.GET.get('categories__slug', None)
    event_category = event_category_slug and get_object_or_404(Category, slug=event_category_slug)
    context = {'event_category': event_category}
    extra_context = extra_context or {}
    context.update(extra_context)
    return content_view(request, event, 'event/event_view.html', extra_context=context)


def event_list(request, year=None, month=None, day=None, queryset=None, extra_context=None):
    filters = {}
    date_day_start = None
    if year and month and day:
        date_day_start = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
        date_day_end = datetime.datetime(int(year), int(month), int(day), 23, 59, 59)
        filters = {'start__lt': date_day_end, 'end__gt': date_day_start}
    events = get_events(request, queryset=queryset).filter(**filters)
    context = {'date': date_day_start}
    extra_context = extra_context or {}
    context.update(extra_context)
    return content_list(request, events,
                        extra_context=context,
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


def get_events(request=None, limit=0, queryset=None):
    queryset = queryset or Event.objects.published()
    events = queryset.order_by("-publish_date")
    qsm = QueryStringManager(request, page_var='page', ignore_params=('set_language', ))
    filters = qsm.get_filters()
    events = events.filter(**filters)
    if limit:
        return events[:limit]
    else:
        return events
