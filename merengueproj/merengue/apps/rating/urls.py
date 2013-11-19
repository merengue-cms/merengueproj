# Copyright (c) 2009 by Yaco Sistemas S.L.
# Contact info: Lorenzo Gil Sanchez <lgs@yaco.es>
#
# This file is part of rating
#
# rating is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rating is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with rating.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import patterns

urlpatterns = patterns('rating.views',
    (r'^rate/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', 'rate_object'),
)
