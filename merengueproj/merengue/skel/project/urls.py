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

# -*- coding: utf-8 -*-
# don't touch this "import *" is necesary for urlresolvers works
from django.conf.urls.defaults import *
from django.conf import settings

from merengue.base import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
     'cmsutils.views.generic.redirect_to_object'),
    (r'^admin/', include(admin.site.urls)),

    # the next admin is only used for having the reverse url running for 'admin'
    url(r'^admin/$', lambda request: '', name="admin_index"),

    # merengue URLs
    (r'^%s/' % settings.MERENGUE_URLS_PREFIX, include('merengue.urls')),

    # merengue media
    (r'^media/(.*)$', 'merengue.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    # Your project URLs. Put here all your URLS:
    (r'^$', 'website.views.index'),
)
