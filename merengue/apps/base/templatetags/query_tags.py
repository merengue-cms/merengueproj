import re

from django import template
from django.contrib.contenttypes.models import ContentType


register = template.Library()


class ObjectListNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = self.get_object_list()
        return ''

    def get_object_list(self):
        raise NotImplementedError


def generic_add_variable_tag(parser, token, node_class):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as ([\w_-]+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag needs an 'as variable_name' parameters" % tag_name
    return node_class(m.group(1))


class ContentTypeBasedNode(ObjectListNode):

    def __init__(self, var_name, content_type):
        super(ContentTypeBasedNode, self).__init__(var_name)
        self.content_type = content_type

    def get_object_list(self):
        return self.content_type.model_class().objects.all()


def generic_content_type_tag(parser, token, node_class):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(?:app_label=)?([\w_-]+)?[\s]*(?:module_name=)?([\w_-]+)?[\s]*as ([\w_-]+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name

    content_type = ContentType.objects.get(app_label=m.group(1), model=m.group(2))

    var_name = m.group(3)
    return node_class(var_name, content_type)


@register.tag
def get_model_objects(parser, token):
    return generic_content_type_tag(parser, token, ContentTypeBasedNode)
