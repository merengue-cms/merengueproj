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


urlpatterns = patterns('plugins.subscription.views',
    url(r'^(?P<basecontent_id>\d+)/$', 'subscription_form', name='subscription_form'),
    url({'en': r'^(?P<basecontent_slug>[\w-]+)/subscribers/$',
         'es': r'^(?P<basecontent_slug>[\w-]+)/subscriptores/$'},
         'subscriber_listing', name='subscriber_listing'),
)
