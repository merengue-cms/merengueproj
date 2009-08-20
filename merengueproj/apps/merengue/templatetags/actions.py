from django import template

from cmsutils.tag_utils import (get_args_and_kwargs,
                                parse_args_kwargs_and_as_var)

from action.actions import ContentAction, SiteAction, UserAction
from action.models import RegisteredAction


register = template.Library()


class GetActionsNode(template.Node):

    def __init__(self, args, kwargs, as_var):
        self.args = args
        self.kwargs = kwargs
        self.as_var = as_var

    def render(self, context):
        args, kwargs = get_args_and_kwargs(self.args, self.kwargs, context)
        scope = kwargs.get('scope')
        # TODO: Support not yet implemented for content types
        for_content = kwargs.get('for', None)
        actions = []
        registered_actions = RegisteredAction.objects.all()
        for registered_action in registered_actions:
            item_class = registered_action.get_registry_item_class()
            if scope == 'site' and issubclass(item_class, SiteAction):
                actions.append(item_class)
            elif scope == 'content' and issubclass(item_class, ContentAction):
                actions.append(item_class)
            elif scope == 'user' and issubclass(item_class, UserAction):
                actions.append(item_class)
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
