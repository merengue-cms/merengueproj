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

import re

from django import template
from django.template.loader import render_to_string

from plugins.core.models import CustomMeta


register = template.Library()


class IfNotCustomMetaNode(template.Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def __repr__(self):
        return "<IfNotCustomMetaNode node>"

    def __iter__(self):
        for node in self.nodelist:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.nodelist.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        request = context['request']
        path = request.META['PATH_INFO']
        for custom in CustomMeta.objects.all():
            reg = re.compile(custom.url_regexp)
            if reg.search(path):
                return render_to_string('core/custommeta.html',
                                        {'custom': custom})
        return self.nodelist.render(context)


@register.tag
def if_not_custommeta(parser, token):
    bits = token.contents.split()
    del bits[0]
    if bits:
        raise template.TemplateSyntaxError("'if_not_custommeta' statement does not expect arguments")
    nodelist = parser.parse(('end_if_not_custommeta', ))
    parser.delete_first_token()
    return IfNotCustomMetaNode(nodelist)
