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


class IfNode(template.Node):
    """ An abstract node for checking things """

    def __init__(self, parser, token):
        bits = list(token.split_contents())
        end_tag = 'end' + bits[0]
        self.if_node = parser.parse(('else', end_tag))
        token = parser.next_token()
        if token.contents == 'else':
            self.else_node = parser.parse((end_tag, ))
            parser.delete_first_token()
        else:
            self.else_node = template.NodeList()

    def __repr__(self):
        return '<IfNode>'

    def check(self, context):
        raise NotImplementedError

    def render(self, context):
        if self.check(context):
            return self.if_node.render(context)
        else:
            return self.else_node.render(context)
