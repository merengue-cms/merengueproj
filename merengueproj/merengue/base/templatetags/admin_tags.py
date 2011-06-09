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
from django.template.loader import render_to_string
from django.utils.translation import ugettext

from classytags.arguments import Argument
from classytags.core import Tag, Options


register = template.Library()


PATHS_SECTIONS = [
    ('pluggable/', 'plugins'),
    ('plugins.', 'plugins'),
    ('block/', 'sitebuilding'),
    ('theming/', 'sitebuilding'),
    ('action/', 'sitebuilding'),
    ('registry/', 'sitebuilding'),
    ('siteconfig/', 'sitebuilding'),
    ('workflow/', 'sitebuilding'),
    ('auth/', 'usermanagement'),
    ('perms/', 'usermanagement'),
]


def main_admin_tabs(context):
    request = context.get('request', None)
    user = request and request.user or None
    path = request.META.get('PATH_INFO', '')
    index = urlresolvers.reverse('admin:index')
    if path.startswith(index):
        path = path.replace(index, '', 1)

    selected = 'contentmanagement'
    for start, section in PATHS_SECTIONS:
        if path.startswith(start):
            selected = section
            break
    return {'selected': selected, 'request': request, 'user': user}
main_admin_tabs = register.inclusion_tag('admin/main_admin_tabs.html', takes_context=True)(main_admin_tabs)


class ObjectToolsTag(Tag):
    name = 'object_tools'
    options = Options(
        Argument('model_admin', resolve=False, required=False),
        Argument('mode', required=False, default='change'),
        Argument('url_prefix', required=False, default=''),
        Argument('obj', required=False),
    )

    def render_tag(self, context, model_admin=None, mode='change', url_prefix='', obj=None):
        request = context['request']
        try:
            model_admin = template.Variable(model_admin).resolve(context)
        except template.VariableDoesNotExist:
            model_admin = None
        # set permissions dictionary with user capabilities adding, changing and deleting
        permissions = {}
        for perm in ('add', 'change', 'delete', ):
            perm_var = 'has_%s_permission' % perm
            permissions[perm] = model_admin and \
                getattr(model_admin, perm_var)(request) or \
                context.get(perm_var, False)

        if obj is None:
            obj = context.get('original', None)
        opts = getattr(obj, '_meta', context.get('opts', None))
        if model_admin is not None:
            object_tools = model_admin.object_tools(request, mode, url_prefix)
        elif mode == 'change':
            object_tools = [
                {'url': url_prefix + 'history/', 'label': ugettext('History'), 'class': 'historylink'},
            ]
        elif mode == 'list':
            object_tools = [
                {'url': url_prefix + 'add/', 'label': ugettext('Add new'),
                 'class': 'addlink', 'permission': 'add'},
            ]
        else:  # mode is 'add'
            object_tools = []
        granted_tools = [tool for tool in object_tools if 'permission' not in tool or
                           permissions[tool['permission']]]
        context = {
            'path': request.META.get('PATH_INFO', ''),
            'request': request,
            'object_tools': granted_tools,
            'opts': opts,
            'object': obj,
            'mode': mode,
            'model_admin': model_admin,
        }
        return render_to_string(
            'admin/object_tools.html', context,
            context_instance=template.RequestContext(request),
        )
register.tag(ObjectToolsTag)
