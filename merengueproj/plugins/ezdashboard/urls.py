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

SLUG_RE = r'[-_\w]+'

urlpatterns = patterns('plugins.ezdashboard.views',
    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^catalog/$', 'gadgets_list', name='catalog'),
    url(r'^meta/(?P<gadget_name>%s)/$' % SLUG_RE, 'gadget_meta',
        name='meta'),
    url(r'^content/(?P<gadget_name>%s)/$' % SLUG_RE, 'gadget_view',
        name='content'),
)
