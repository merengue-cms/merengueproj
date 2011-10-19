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
import datetime
import os

from django import template
from django.contrib.admin.options import IncorrectLookupParameters
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.utils.dates import WEEKDAYS, MONTHS

from merengue.base.admin import PluginAdmin
from merengue.multimedia.admin import BaseMultimediaAdmin, VideoAdmin
from merengue.perms.exceptions import PermissionDenied
from plugins.tv.models import Channel, Schedule, VideoStreaming


WEEK_HOURS_DELTA = datetime.timedelta(minutes=30)


class ChannelAdmin(PluginAdmin):
    pass


class ScheduleAdmin(PluginAdmin):
    week_view_template = 'tv/admin/tv/schedule/week_view.html'
    day_view_template = 'tv/admin/tv/schedule/day_view.html'
    list_display = ('get_video_name', 'broadcast_date', 'get_weekday', 'get_start_seconds', 'get_end_seconds')
    actions = None
    ordering = ('-broadcast_date', )
    date_hierarchy = 'broadcast_date'

    def get_video_name(self, obj):
        html = '<div class="video-name">%s</div>' % obj.video.name
        html += '<div class="video-preview">'
        if obj.video.preview and obj.video.preview.thumbnail and os.path.exists(obj.video.preview.thumbnail.path()):
            html += '<img src="%s" />' % obj.video.preview.thumbnail.url()
        html += '</div>'
        html += '<span class="schedule_id hide">%s</span>' % obj.id
        html += '<div class="video-start">%s</div>' % obj.broadcast_date.strftime('%H:%Mh')
        video_end = obj.broadcast_date + datetime.timedelta(seconds=obj.video.duration)
        html += '<div class="video-end">%s</div>' % video_end.strftime('%H:%Mh')
        html += '<br style="clear: both;">'
        return html
    get_video_name.allow_tags=True

    def get_weekday(self, obj):
        return obj.broadcast_date.weekday()
    get_weekday.short_description = 'weekday'

    def get_start_seconds(self, obj):
        delta = obj.broadcast_date - datetime.datetime(obj.broadcast_date.year,
                                                       obj.broadcast_date.month,
                                                       obj.broadcast_date.day)
        return delta.seconds
    get_start_seconds.short_description = 'start seconds'

    def get_end_seconds(self, obj):
        return self.get_start_seconds(obj) + obj.video.duration
    get_end_seconds.short_description = 'end seconds'

    def get_changelist(self, request, extra_context):
        from django.contrib.admin.views.main import ChangeList
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        request_init_week = request.GET.get('broadcast_date__gte', None)

        if not request_init_week:
            today = datetime.date.today()
            init_week = today - datetime.timedelta(today.weekday())
            end_week = init_week + datetime.timedelta(7)
        else:
            init_week = datetime.datetime.fromordinal(int(request_init_week)).date()
            end_week = init_week + datetime.timedelta(7)
        request.GET.update({'broadcast_date__gte': init_week,
                            'broadcast_date__lt': end_week,
                            })

        cl = ChangeList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
            self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_editable, self)
        return cl

    def get_hours(self, delta):
        begin = init = datetime.datetime(1, 1, 1)
        end = datetime.datetime(1, 1, 2)
        hours = []
        while init < end:
            hours.append({'hour': init.time(),
                          'seconds_of_day': (init-begin).seconds,
                         })
            init = init + delta
        return hours

    def get_days(self, start_date):
        days = []
        for key, value in WEEKDAYS.items():
            date = start_date + datetime.timedelta(key)
            field = 'broadcast_date'
            days.append({'name': value,
                         'index': key,
                         'date': date,
                         'datefilter': '%(field)s__year=%(year)s&%(field)s__month=%(month)s&%(field)s__day=%(day)s' % {
                            'field': field,
                            'year': date.year,
                            'month': date.month,
                            'day': date.day,
                            },
                        })
        return days

    def week_view(self, request, extra_context=None):
        from django.contrib.admin.views.main import ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label

        try:
            cl = self.get_changelist(request, extra_context)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        cl.formset = None
        start_date = request.GET.get('broadcast_date__gte')
        end_date = request.GET.get('broadcast_date__lt')
        context = {
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
            'days': self.get_days(start_date),
            'hours': self.get_hours(WEEK_HOURS_DELTA),
            'hoursdelta': WEEK_HOURS_DELTA.seconds,
            'actual_date': 'Del %s de %s de %s al  %s de %s de %s' % (start_date.day, smart_str(MONTHS[start_date.month]), start_date.year,
                end_date.day, smart_str(MONTHS[end_date.month]), end_date.year),
            'base_date': start_date,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.week_view_template,
                                  context, context_instance=context_instance)

    def day_view(self, request, extra_context=None):
        from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label
        reduced_view = request.GET.pop('reduced_view', False)

        try:
            cl = ChangeList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_editable, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        cl.formset = None
        day = int(request.GET.get('broadcast_date__day'))
        month = int(request.GET.get('broadcast_date__month'))
        year = int(request.GET.get('broadcast_date__year'))
        day = datetime.datetime(year, month, day)
        context = {
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
            'actual_date': '%s de %s de %s' % (day.day, smart_str(MONTHS[day.month]), day.year),
            'days': [{'name': WEEKDAYS[day.weekday()],
                      'index': day.weekday(),
                      'date': day.date(),
                     }],
            'hours': self.get_hours(WEEK_HOURS_DELTA),
            'hoursdelta': WEEK_HOURS_DELTA.seconds,
            'reduced_view': reduced_view,
            'base_date': day,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.day_view_template,
                                  context, context_instance=context_instance)

    def changelist_view(self, request, extra_context=None):
        if request.is_ajax():
            return self.change_schedule_date(request)

        if request.GET.get('broadcast_date__day', None):
            return self.day_view(request, extra_context)
            return super(ScheduleAdmin, self).changelist_view(request, extra_context)
        return self.week_view(request, extra_context)

    def change_schedule_date(self, request):
        date = request.GET.get('date', None)
        schedule_id = request.GET.get('schedule_id', None)

        if not date or not schedule_id:
            raise Http404

        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            raise Http404

        schedule.broadcast_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        schedule.save()

        start_date = schedule.broadcast_date.strftime('%H:%Mh')
        video_end = schedule.broadcast_date + datetime.timedelta(seconds=schedule.video.duration)
        end_date = video_end.strftime('%H:%Mh')

        json = simplejson.dumps({'start_date': start_date,
                                 'end_date': end_date,
                                }, ensure_ascii=False)
        return HttpResponse(json, 'text/javascript')


class VideoStreamingAdmin(VideoAdmin):

    exclude = ('authors', 'file', 'external_url')

    def get_form(self, request, obj=None):
        form = super(BaseMultimediaAdmin, self).get_form(request, obj)

        def clean(self):
            super(form, self).clean()
            return self.cleaned_data
        form.clean = clean
        return form


def register(site):
    """ Merengue admin registration callback """
    site.register(Channel, ChannelAdmin)
    site.register(Schedule, ScheduleAdmin)
    site.register(VideoStreaming, VideoStreamingAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Channel)
    site.unregister(Schedule)
    site.unregister(VideoStreaming)
