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

from merengue.base.templatetags import IfNode
from merengue.perms.utils import has_permission, has_global_permission


register = template.Library()


class PermissionComparisonNode(template.Node):
    """Implements a node to provide an if current user has passed permission
    for current object.
    """

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.contents.split()
        if len(bits) not in (2, 3):
            raise template.TemplateSyntaxError(
                "'%s' tag takes one or two arguments" % bits[0])
        end_tag = 'endifhasperm'
        nodelist_true = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else':  # there is an 'else' clause in the tag
            nodelist_false = parser.parse((end_tag, ))
            parser.delete_first_token()
        else:
            nodelist_false = ""
        val = parser.compile_filter(bits[1])
        if len(bits) == 3:
            obj = template.Variable(bits[2])
        else:
            obj = None
        return cls(val, obj, nodelist_true, nodelist_false)

    def __init__(self, permission, obj, nodelist_true, nodelist_false):
        self.permission = permission
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.obj = obj

    def render(self, context):
        if not self.obj:
            obj = context.get("obj") or context.get("content")
        else:
            obj = self.obj.resolve(context)
        request = context.get("request")
        permission = self.permission.resolve(context, True)
        if obj:
            has_perm = has_permission(obj, request.user, permission)
        else:
            has_perm = has_global_permission(request.user, permission)

        if has_perm:
            return self.nodelist_true.render(context)
        else:
            if self.nodelist_false:
                return self.nodelist_false.render(context)
            return ''


@register.tag
def ifhasperm(parser, token):
    """This function provides functionality for the 'ifhasperm' template tag.
    Usage::
      {% ifhasperm "edit" %}
    Or:
      {% ifhasperm "edit" obj %}
    """
    return PermissionComparisonNode.handle_token(parser, token)


class IfCanEditNode(IfNode):

    def __init__(self, user, content, *args):
        self.content = content
        self.user = user
        super(IfCanEditNode, self).__init__(*args)

    def check(self, context):
        content = template.Variable(self.content).resolve(context)
        user = template.Variable(self.user).resolve(context)
        return bool(content.can_edit(user))


def ifcanedit(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise template.TemplateSyntaxError, '%r takes two arguments' % bits[0]
    user = bits[1]
    content = bits[2]
    return IfCanEditNode(user, content, parser, token)
ifcanedit = register.tag(ifcanedit)
