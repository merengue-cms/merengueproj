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

from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404
from django.utils.simplejson import dumps

from merengue.base.views import content_view
from merengue.collection.models import Collection
from merengue.collection.views import collection_view

from plugins.event.models import Event, Category
from plugins.event.utils import getEventsMonthYear


EVENT_COLLECTION_SLUG = 'event'


def event_view(request, event_slug, extra_context=None, template_name='event_view.html'):
    event = get_object_or_404(Event, slug=event_slug)
    event_category_slug = request.GET.get('categories__slug', None)
    event_category = event_category_slug and get_object_or_404(Category, slug=event_category_slug)
    context = {'event_category': event_category}
    extra_context = extra_context or {}
    context.update(extra_context)
    return content_view(request, event, template_name, extra_context=context)


def event_list(request, year=None, month=None, day=None, queryset=None,
               extra_context=None,
               template_name='event_list.html'):
    filters = {}
    date_day_start = None
    event_collection = get_collection_event()

    if year and month and day:
        try:
            date_day_start = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
            date_day_end = datetime.datetime(int(year), int(month), int(day), 23, 59, 59)
        except ValueError:
            raise Http404
        filters = Q(start__lt=date_day_end,
                    end__gt=date_day_start)
    else:
        today = datetime.datetime.now()
        filters = Q(start__gte=today) | Q(end__gte=today)

    context = {'date': date_day_start, '_filters_collection': filters}
    extra_context = extra_context or {}
    context.update(extra_context)
    return collection_view(request, event_collection, extra_context=context, template_name=template_name)


def event_historic(request, queryset=None, extra_context=None,
                   template_name='event_historic.html'):
    filters = {}
    event_collection = get_collection_event()

    today = datetime.datetime.now()
    filters = Q(end__lte=today)

    context = {'_filters_collection': filters,
               '_group_by_collection': None,
               '_order_by_collection': '-end'}
    extra_context = extra_context or {}
    context.update(extra_context)
    return collection_view(request, event_collection, extra_context=context, template_name=template_name)


def events_calendar(request):
    mimetype = "application/json"
    if (request.GET and 'month' in request.GET
        and 'year' in request.GET):
        month = int(request.GET['month'])
        year = int(request.GET['year'])
        events = get_events(request)
        events_dic = getEventsMonthYear(month, year, events)
        return HttpResponse(dumps(events_dic), mimetype=mimetype)
    return HttpResponseBadRequest(mimetype=mimetype)


def get_events(request=None, limit=None, queryset=None, filtering_section=None):
    if queryset:
        return queryset
    collection = get_collection_event()
    section = None
    if request and request.section:
        section = request.section
    return collection.get_items(section, filtering_section)[:limit]


def get_collection_event():
    return Collection.objects.get(
        slug=EVENT_COLLECTION_SLUG)
