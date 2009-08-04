from django import template
from django.contrib.contenttypes.models import ContentType

import re

register = template.Library()


class ContentTypeNode(template.Node):

    def __init__(self, content, var_name):
        self.content = content
        self.var_name = var_name

    def render(self, context):
        content = context.get(self.content, None)
        if not content:
            return ''
        context[self.var_name] = ContentType.objects.get_for_model(content)
        return ''


def get_content_type(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'([^ ]*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    content, var_name = m.groups()
    return ContentTypeNode(content, var_name)

register.tag('content_type', get_content_type)


class MetaOfContentTypeNode(template.Node):

    def __init__(self, content, var_name):
        self.content = content
        self.var_name = var_name

    def render(self, context):
        content = context.get(self.content, None)
        if not content:
            return ''
        context[self.var_name] = content.model_class()._meta
        return ''


def get_meta_of_content_type(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'([^ ]*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    content_type, var_name = m.groups()
    return MetaOfContentTypeNode(content_type, var_name)

register.tag('get_meta_of_content_type', get_meta_of_content_type)
