import re

from django import template

register = template.Library()


class FirstOfNode(template.Node):

    def __init__(self, vars_input, var_output):
        self.vars_input = vars_input
        self.var_output = var_output

    def render(self, context):
        vars_input_list = self.vars_input.split(' ')
        for var_input in vars_input_list:
            value_var_input = self.get_value(context, var_input)
            if value_var_input:
                context[self.var_output] = value_var_input
                break
        return ''

    def get_value(self, context, var_input, value=None):
        var_input_split = var_input.split('.')
        if len(var_input_split) == 1:
            if not value:
                return context.get(var_input)
            else:
                return getattr(value, var_input)
        else:
            var_value = var_input_split[0]
            del var_input_split[0]
            var_input = '.'.join(var_input_split)
            value = context.get(var_value)
            return self.get_value(context, var_input, value)

    def get_object_list(self):
        raise NotImplementedError


def generic_content_type_tag(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(([\.\w_-]+ )+)as ([\w_-]+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name

    vars_input = m.group(1)

    var_output = m.group(3)
    return FirstOfNode(vars_input, var_output)


@register.tag
def first_of_with_as(parser, token):
    return generic_content_type_tag(parser, token)
