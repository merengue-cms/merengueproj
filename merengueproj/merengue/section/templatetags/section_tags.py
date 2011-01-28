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
from django.core.urlresolvers import reverse, NoReverseMatch

from django.utils.translation import ugettext_lazy as _

from mptt.utils import tree_item_iterator

from merengue.section.models import Menu


register = template.Library()


@register.inclusion_tag('section/menu_tag.html', takes_context=True)
def menu_tag(context, menu, descendants=None):
    ancestors = []
    menu_item = None
    if descendants is None:
        descendants = menu.get_descendants()
    try:
        menuitem_slug = context['request'].META['PATH_INFO'].split('/')[-2]
        try:
            menu_item = descendants.get(slug=menuitem_slug)
            ancestors = menu_item.get_ancestors()[1:]
        except Menu.DoesNotExist:
            pass
    except IndexError:
        pass

    context = copy.copy(context)
    context.update({'menu': menu,
                    'user': context.get('user', None),
                    'menu_item': menu_item,
                    'menu_item__level': menu_item and menu_item.level or 1,
                    'ancestors': ancestors})
    return context


@register.inclusion_tag('section/menu_portal_tag.html', takes_context=True)
def menu_portal_tag(context, menu):
    return menu_tag(context, menu)


@register.inclusion_tag('section/menu_sitemap_tag.html', takes_context=True)
def menu_sitemap_tag(context, section, class_ul):
    new_context = {}
    new_context['class_ul'] = class_ul
    menu_tree = []
    user = context['request'].user
    if user.is_staff or section.status == 2:
        get_menu_iterative(context, section.main_menu, menu_tree)
        get_static_main_menu(context, section, menu_tree)
        get_menu_agenda(context, section, menu_tree)
        new_context['menu_tree'] = menu_tree
    return new_context


def get_menu_iterative(context, menu, menu_tree):
    user = context['request'].user
    children = tree_item_iterator(menu.get_descendants())
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


def get_menu_agenda(context, section, menu_tree):
    menu_child = {}
    if (section.category_set.all() or section.categorygroup_set.all()):
        try:
            menu_child['name'] = _('Agenda')
            menu_child['slug'] = 'agenda-%s' % section.slug
            menu_child['url'] = section.get_agenda_url()
            menu_child['deep'] = 0
            menu_child['new_level'] = True
            menu_child['end_level'] = range(True)
            menu_tree.append(menu_child)
        except NoReverseMatch:
            pass


def get_static_main_menu(context, section, menu_tree):
    menu_child = {}
    try:
        converter_app_name = {'golf': 'course',
                                'leisure': None,
                                'photocontests': 'contestant',
                                'sport': 'sport_facility'}
        app_name = section.app_name
        if app_name in converter_app_name:
            app_name = converter_app_name[app_name]
        if app_name:
            url_search = reverse('%s_search' % app_name)
            menu_child['name'] = _('Searcher')
            menu_child['slug'] = 'search-%s' % section.slug
            menu_child['url'] = url_search
            menu_child['deep'] = 0
            menu_child['new_level'] = True
            menu_child['end_level'] = range(True)
            menu_tree.append(menu_child)
    except NoReverseMatch:
        pass
