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

from django.conf.urls.defaults import patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('merengue.base.views',
    (r'^admin_redirect/(?P<content_type>\d+)/(?P<content_id>\d+)/(?P<url>.*)$', 'admin_link'),
    (r'^public_redirect/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<content_id>\d+)/$', 'public_link'),
    (r'^view/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<content_id>\d+)/(?P<content_slug>[\w-]+)/$', 'public_view'),
    (r'^ajax/autocomplete/tags/(?P<app_name>.*)/(?P<model>.*)/$', 'ajax_autocomplete_tags'),
)
