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

import copy

from django import template
from django.db.models import Q
from django.core.urlresolvers import reverse, NoReverseMatch

from django.utils.translation import ugettext_lazy as _

from mptt.utils import tree_item_iterator

from merengue.section.models import Menu


register = template.Library()


@register.inclusion_tag('section/menu_tag.html', takes_context=True)
def menu_tag(context, menu, max_num_level=-1, descendants=None):
    ancestors = []
    menu_item = None
    user = context['request'].user
    if not descendants:
        descendants = menu.get_descendants_by_user(user)
    try:
        allmenuitems = [e for e in context['request'].META['PATH_INFO'].split('/') if e]
        menu_items_slug = descendants.filter(slug__in=allmenuitems)
        if menu_items_slug:
            menuitem_slug = allmenuitems[-1]
            try:
                menu_item = descendants.get(slug=menuitem_slug)
                ancestors = menu_item.get_ancestors_by_user(user)
            except Menu.DoesNotExist:
                # Try to get the last item in path which will be the selected menu item.
                for item in allmenuitems[:-1]:
                    try:
                        menu_item = descendants.get(slug=item)
                        ancestors = menu_item.get_ancestors_by_user(user)
                    except Menu.DoesNotExist:
                        pass
    except IndexError:
        pass

    if max_num_level != -1:
        if not menu_item:
            menu_item = menu
            min_level = 1
        else:
            current_level = menu_item.level
            if current_level == 0:
                current_level = 1
            min_level = current_level - (current_level - 1) % max_num_level
            menu = ancestors.get(level=min_level - 1)
        max_level = min_level + max_num_level - 1
        descendants = menu.get_descendants_by_user(user).filter(Q(level__gte=min_level,
                                                                  level__lte=max_level) |
                                                                Q(level=menu_item.level + 1,
                                                                  parent=menu_item))
    else:
        min_level = None
        max_level = None
    context = copy.copy(context)
    context.update({'menu': menu,
            'menu_items': descendants.select_related('baselink__absolutelink', 'baselink__contentlink', 'baselink__viewletlink'),
            'menu_item': menu_item,
            'menu_item__level': menu_item and menu_item.level or 1,
            'ancestors': ancestors,
            'min_level': min_level,
            'max_level': max_level})
    return context


@register.inclusion_tag('section/menu_portal_tag.html', takes_context=True)
def menu_portal_tag(context, menu, max_num_level=-1):
    return menu_tag(context, menu, max_num_level)


@register.inclusion_tag('section/menu_sitemap_tag.html', takes_context=True)
def menu_sitemap_tag(context, section, class_ul):
    new_context = {}
    new_context['class_ul'] = class_ul
    menu_tree = []
    user = context['request'].user
    if user.is_staff or section.status == 2:
        get_menu_iterative(context, section.main_menu, menu_tree)
        get_static_main_menu(context, section, menu_tree)
        new_context['menu_tree'] = menu_tree
    return new_context


def get_menu_iterative(context, menu, menu_tree):
    user = context['request'].user
    children = tree_item_iterator(menu.get_descendants_by_user(user))
    if children:
        for child, options in children:
            if user.is_staff or child.is_published():
                menu_child = {}
                menu_child['name'] = child.name
                menu_child['slug'] = child.slug
                menu_child['url'] = child.get_absolute_url()
                new_level = options['new_level']
                closed_levels = options['closed_levels']
                if child.level in closed_levels:
                    len_closed_levels = len(closed_levels)
                    if child.level == 1:
                        len_closed_levels -= 1
                    menu_child['end_level'] = range(len_closed_levels)
                else:
                    menu_child['end_level'] = range(False)
                menu_child['new_level'] = new_level
                menu_tree.append(menu_child)


def get_static_main_menu(context, section, menu_tree):
    menu_child = {}
    try:
        if section.app_name:
            url_search = reverse('%s_search' % section.app_name)
            menu_child['name'] = _('Searcher')
            menu_child['slug'] = 'search-%s' % section.slug
            menu_child['url'] = url_search
            menu_child['deep'] = 0
            menu_child['new_level'] = True
            menu_child['end_level'] = range(True)
            menu_tree.append(menu_child)
    except NoReverseMatch:
        pass


class SectionBreadcrumbsNode(template.Node):

    def __init__(self, section=None, content=None):
        self.content = content
        self.section = section

    def render(self, context):
        section = self.section and context.get(self.section, None)
        content = self.content and context.get(self.content, None)
        if section:
            return section.get_real_instance().breadcrumbs(content)
        else:
            return content.get_real_instance().breadcrumbs()


def section_breadcrumbs(parser, token):
    try:
        tag_name, section, content = token.split_contents()
    except ValueError:
        try:
            tag_name, section = token.split_contents()
            content = None
        except ValueError:
            raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    return SectionBreadcrumbsNode(section, content)

register.tag('section_breadcrumbs_tag', section_breadcrumbs)


class URLInSectionBreadcrumbsNode(template.Node):

    def __init__(self, section, url, var_name=None):
        self.url = url
        self.section = section
        self.var_name = var_name

    def render(self, context):
        section = context.get(self.section, None)
        url = context.get(self.url, None)
        url_in_section = section and section.get_real_instance().url_in_section(url)
        if self.var_name:
            context[self.var_name] = url_in_section
            return ''
        return url_in_section


def url_in_section_breadcrumbs(parser, token):
    try:
        tag_name, section, url = token.split_contents()
        var_name = None
    except ValueError:
        try:
            tag_name, section, url, _as, var_name = token.split_contents()
        except ValueError:
            raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    return URLInSectionBreadcrumbsNode(section, url, var_name)

register.tag('url_in_section_breadcrumbs_tag', url_in_section_breadcrumbs)
