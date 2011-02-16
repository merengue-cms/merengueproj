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

from django import template
from django.core import urlresolvers

register = template.Library()


PATHS_SECTIONS = [
    ('plugins.', 'plugins'),
    ('block/', 'sitebuilding'),
    ('pluggable/', 'sitebuilding'),
    ('theming/', 'sitebuilding'),
    ('action/', 'sitebuilding'),
    ('registry/', 'sitebuilding'),
    ('siteconfig/', 'sitebuilding'),
    ('auth/', 'usermanagement'),
    ('perms/', 'usermanagement'),
]


def main_admin_tabs(context):
    request = context.get('request', None)
    path = request.META.get('PATH_INFO', '')
    index = urlresolvers.reverse('admin:index')
    if path.startswith(index):
        path = path.replace(index, '', 1)

    selected = 'contentmanagement'
    for start, section in PATHS_SECTIONS:
        if path.startswith(start):
            selected = section
            break
    return {'selected': selected}
main_admin_tabs = register.inclusion_tag('admin/main_admin_tabs.html', takes_context=True)(main_admin_tabs)
