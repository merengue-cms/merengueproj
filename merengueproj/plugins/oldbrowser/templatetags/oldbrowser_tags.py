# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from plugins.oldbrowser.models import OldBrowser


register = template.Library()


class OldBrowserNode(template.Node):

    def render(self, context):

        request = context['request']
        user_agent = request.META['HTTP_USER_AGENT']
        for oldbrowser in OldBrowser.objects.all():
            if re.search(oldbrowser.user_agent, user_agent):
                warning_string = _(u'Your browser is too old. Please, update it.')
                if settings.DEBUG:
                    warning_string = u'(%s) %s' % (oldbrowser.user_agent,
                                                   warning_string)
                return warning_string

        return ''


def old_browser(parser, token):
    if len(token.split_contents()) > 1:
        raise template.TemplateSyntaxError, "%r takes no arguments"\
              % token.contents.split()[0]
    return OldBrowserNode()


register.tag('oldbrowser', old_browser)


class IfOldBrowserNode(template.Node):

    def __init__(self, if_node, else_node):
        self.if_node = if_node
        self.else_node = else_node
        self.bad_user_agent = ''

    def __repr__(self):
        return '<IfNode>'

    def check(self, context):
        request = context['request']
        user_agent = request.META['HTTP_USER_AGENT']
        for oldbrowser in OldBrowser.objects.all():
            if re.search(oldbrowser.user_agent, user_agent):
                self.bad_user_agent = oldbrowser.user_agent
                return True
        return False

    def render(self, context):
        if self.check(context):
            context['bad_user_agent'] = self.bad_user_agent
            return self.if_node.render(context)
        else:
            return self.else_node.render(context)


def ifoldbrowser(parser, token):
    bits = token.split_contents()
    if len(bits) != 1:
        raise template.TemplateSyntaxError, '%r takes no arguments' % bits[0]
    end_tag = 'end' + bits[0]
    node_ismanager = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        node_notismanager = parser.parse((end_tag, ))
        parser.delete_first_token()
    else:
        node_notismanager = template.NodeList()
    return IfOldBrowserNode(node_ismanager, node_notismanager)


register.tag('ifoldbrowser', ifoldbrowser)
