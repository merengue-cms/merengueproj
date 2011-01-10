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

from merengue.base.templatetags import IfNode

register = template.Library()


@register.inclusion_tag('base/content_title.html', takes_context=True)
def can_edit(context, content):
    return {'content': content, 'request': context.get('request')}


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
