# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.event.views',
    url(r'^$', 'event_list', name='event_list'),
    url(r'^(?P<event_slug>[\w-]+)/$', 'event_view', name='event_view'),
    url(r'^(?P<year>[\d-]+)/(?P<month>[\d-]+)/(?P<day>[\d-]+)/$', 'event_list', name='event_list'),
    url(r'^calendar/ajax/$', 'events_calendar', name='events_calendar'),
)
