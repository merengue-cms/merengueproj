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

from plugins.news.config import PluginConfig
from plugins.news.models import NewsCategory, NewsItem


register = template.Library()


class NewsCategoryNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = NewsCategory.objects.filter(newsitem__isnull=False).distinct()
        return ''


def get_news_category(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    return NewsCategoryNode(m.groups()[0])
register.tag('get_news_category', get_news_category)


class NewsItemNode(template.Node):

    def __init__(self, var_name, category):
        self.var_name = var_name
        self.category = category

    def render(self, context):
        category = context[self.category]
        newsitems = NewsItem.objects.published().filter(categories=category).distinct()
        limit = PluginConfig.get_config().get('limit', None)
        if limit:
            newsitems = newsitems[:int(limit.value)]
        context[self.var_name] = newsitems
        return ''


def get_news_of_category(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'([^ ]*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    category, var_name = m.groups()
    return NewsItemNode(var_name, category)
register.tag('get_news_of_category', get_news_of_category)
