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

from cmsutils.tag_utils import (get_args_and_kwargs,
                                parse_args_kwargs_and_as_var)

from merengue.action.actions import ContentAction, SiteAction, UserAction
from merengue.action.models import RegisteredAction


register = template.Library()


class GetActionsNode(template.Node):

    def __init__(self, args, kwargs, as_var):
        self.args = args
        self.kwargs = kwargs
        self.as_var = as_var

    def render(self, context):
        args, kwargs = get_args_and_kwargs(self.args, self.kwargs, context)
        scope = kwargs.get('scope')
        for_content = kwargs.get('for', None)
        actions = []
        registered_actions = RegisteredAction.objects.actives()
        for registered_action in registered_actions:
            item = registered_action.get_registry_item()
            if scope == 'site' and isinstance(item, SiteAction):
                actions.append(item)
            elif for_content and scope == 'content' and isinstance(item, ContentAction):
                actions.append(item)
            elif for_content and scope == 'user' and isinstance(item, UserAction):
                actions.append(item)
        context[self.as_var] = actions
        return u''


@register.tag
def get_actions(parser, token):
    args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, token)
    args_len = len(args)
    if args_len > 0:
        kwargs['scope'] = args[0]
    if args_len == 3:
        kwargs['for'] = args[2]
    args = []
    return GetActionsNode(args, kwargs, as_var)


class ActionURLNode(template.Node):

    def __init__(self, action, content_or_user, variable_context):
        self.action = action
        self.content_or_user = content_or_user
        self.variable_context = variable_context

    def render(self, context):
        context[self.variable_context] = None
        request = context['request']
        if self.content_or_user is not None:
            content_or_user = self.content_or_user.resolve(context)
        else:
            content_or_user = None
        action = self.action.resolve(context)
        action_link = None
        if content_or_user:
            if action.has_action(request, content_or_user):
                action_link = action.get_url(request, content_or_user)
        else:
            if action.has_action(request):
                action_link = action.get_url(request)
        context[self.variable_context] = action_link
        return ''


@register.tag
def action_url(parser, token):
    bits = token.split_contents()
    if len(bits) not in [4, 5, ]:
        raise template.TemplateSyntaxError('"%r" tag requires one or two arguments' % bits[0])
    action = parser.compile_filter(bits[1])
    if len(bits) == 4:
        content_or_user = None
        variable_context = bits[3]
    else:
        content_or_user = parser.compile_filter(bits[2])
        variable_context = bits[4]
    return ActionURLNode(action, content_or_user, variable_context)
