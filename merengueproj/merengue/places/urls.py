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
from merengue.urlresolvers import merengue_url as url


urlpatterns = patterns('merengue.places.views',
    url({'en': r'^ajax/nearby/$',
         'es': r'^ajax/cercano/$'},
         'places_ajax_nearby', name='places_ajax_nearby'),
    url({'en': r'^merengue_content_info/(?P<content_type>\d+)/(?P<content_id>\d+)/$',
         'es': r'^merengue_informacion_contenido/(?P<content_type>\d+)/(?P<content_id>\d+)/$'},
         'content_info', name='content_info'),
)
