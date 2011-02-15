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

urlpatterns = patterns('merengue.action.views',
    url({'en': r'site/(?P<name>.*)/',
         'es': r'sitio/(?P<name>.*)/'},
        'site_action', name='site_action'),
    url({'en': r'user/(?P<username>.*)/(?P<name>.*)/',
         'es': r'usuario/(?P<username>.*)/(?P<name>.*)/'},
         'user_action', name='user_action'),
    url({'en': r'content/(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<name>.*)/',
         'es': r'contenido/(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<name>.*)/'},
         'content_action', name='content_action'),
)
