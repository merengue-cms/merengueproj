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


urlpatterns = patterns('plugins.registration.views',
    url(r'^$', 'register_view', name='register_view'),
    url({'en': r'^confirm/(?P<username>[\w.@+-]+)/(?P<registration_hash>[a-f0-9]+)/$',
         'es': r'^confirmar/(?P<username>[\w.@+-]+)/(?P<registration_hash>[a-f0-9]+)/$'}, 'confirm_register_view', name='confirm_register_view'),
    url({'en': r'^password_recovery/$',
         'es': r'^recuperar_clave/$'}, 'password_recovery_view', name='password_recovery_view'),
    url({'en': r'^password_recovery/confirm/(?P<username>[\w.@+-]+)/(?P<recovery_hash>[a-f0-9]+)/$',
         'es': r'^recuperar_clave/confirmar/(?P<username>[\w.@+-]+)/(?P<recovery_hash>[a-f0-9]+)/$'}, 'confirm_password_recovery', name='confirm_password_recovery'),
    url(r'^ajax/check_username/$', 'ajax_check_username', name='ajax_check_username'),
)
