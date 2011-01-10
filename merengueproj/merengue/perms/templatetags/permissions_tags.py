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

# django imports
from django import template

import merengue.perms.utils
register = template.Library()


class PermissionComparisonNode(template.Node):
    """Implements a node to provide an if current user has passed permission
    for current object.
    """

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.contents.split()
        if len(bits) != 2:
            raise template.TemplateSyntaxError(
                "'%s' tag takes one argument" % bits[0])
        end_tag = 'endifhasperm'
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else': # there is an 'else' clause in the tag
            nodelist_false = parser.parse((end_tag, ))
            parser.delete_first_token()
        else:
            nodelist_false = ""
        val = parser.compile_filter(bits[1])

        return cls(val, nodelist_true, nodelist_false)

    def __init__(self, permission, nodelist_true, nodelist_false):
        self.permission = permission
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        obj = context.get("obj") or context.get("content")
        request = context.get("request")
        self.permission = self.permission.resolve(context, True)
        if obj:
            has_perm = merengue.perms.utils.has_permission(obj, request.user, self.permission)
        else:
            has_perm = merengue.perms.utils.has_global_permission(request.user, self.permission)

        if has_perm:
            return self.nodelist_true.render(context)
        else:
            if self.nodelist_false:
                return self.nodelist_false.render(context)
            return ''


@register.tag
def ifhasperm(parser, token):
    """This function provides functionality for the 'ifhasperm' template tag.
    """
    return PermissionComparisonNode.handle_token(parser, token)
