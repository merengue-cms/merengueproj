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
