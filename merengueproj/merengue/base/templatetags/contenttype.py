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
