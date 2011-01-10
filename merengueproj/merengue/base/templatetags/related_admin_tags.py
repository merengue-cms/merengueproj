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
from django.core import urlresolvers
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext as _

register = template.Library()


def _calculate_route(context, only_initial=False):
    model_admin = context.get('model_admin', None)
    model_admin_visited = []
    if model_admin:
        admin_site = model_admin.admin_site
        original = context.get('original', None) or context.get('object', None)
        site_list = [{'opts': model_admin.opts,
                      'obj': original,
                      'admin': model_admin,
                      'site': model_admin.admin_site,
                      'tool_name': None,
                     }]
        if only_initial:
            return site_list
        request = context.get('request', None)
        visited = []
        if request:
            visited = getattr(request, '__visited__', [])
        if not visited:
            return site_list
        for model_admin, basecontent in visited:
            site_list += [{'opts': model_admin.opts,
                           'admin': model_admin,
                           'site': model_admin.admin_site,
                           'obj': basecontent,
                           'tool_name': getattr(model_admin, 'tool_name', None),
                        }]
        site_list.reverse()
        return site_list
    return None


def advanced_breadcrumbs(context):
    add = context.get('add', None)
    route = _calculate_route(context)
    if not route:
        route = [{'admin': None,
                  'obj': context.get('original'),
                  'opts': context.get('opts') or context.get('cl').opts,
                  'site': None,
                  'tool_name': None}]
    url_list = []

    if route:
        try:
            url_list = [{'label': _('Home'),
                        'url': urlresolvers.reverse('admin:index'),
                        }]
            if getattr(route[0]['site'], 'i_am_plugin_site', False):
                url_list += [{'label': _('%(plugin_name)s plugin') % {'plugin_name': route[0]['site'].plugin_name.title()},
                            'url': url_list[0]['url'] + route[0]['site'].prefix + '/',
                            }]
            url_list += [{'label': _(route[0]['opts'].app_label.title()),
                        'url': url_list[-1]['url'] + route[0]['opts'].app_label,
                        },
                        {'label': _(route[0]['opts'].verbose_name_plural.title()),
                        'url': url_list[-1]['url'] + route[0]['opts'].app_label + '/' + route[0]['opts'].module_name,
                        }]
            if route[0]['obj']:
                url_list += [{'label':route[0]['obj'],
                            'url': "%s/%s/" %(url_list[-1]['url'], route[0]['obj'].id),
                            }]
            elif add:
                url_list += [{'label': _('Add'),
                            'url': "%s/add/" %(url_list[-1]['url']),
                            }]
            base_url = url_list[-1]['url']

            for r in route[1:]:
                model_admin = r['admin']
                if not model_admin.one_to_one:
                    # in one to one related models, we hide listings
                    url_list += [{'label': _(r['admin'].tool_label),
                                'url': base_url + r['admin'].tool_name + '/',
                                }]
                if r['obj']:
                    url_list += [{'label': r['obj'],
                                'url': base_url + r['admin'].tool_name + '/'+ str(r['obj'].id) + '/',
                                }]
                elif add:
                    url_list += [{'label': _('Add'),
                                'url': base_url + r['admin'].tool_name + '/' + '/add/',
                                }]
                base_url = url_list[-1]['url']
        except NoReverseMatch:
            pass
    return {'url_list': url_list,
           }
advanced_breadcrumbs = register.inclusion_tag('admin/advanced_breadcrumbs.html', takes_context=True)(advanced_breadcrumbs)


def _get_url_for_model(model):
    return '%s/%s/' % (model._meta.app_label, model._meta.module_name)


def _smart_relations_object_tool_admin_site(admin_site, model_admin, obj, tool_name, tools=None, tools_url=None):
    tools = tools or []
    tools_admin_site = []
    tools_url = tools_url or []

    for cl in obj.__class__.__mro__:
        related = admin_site.related_registry.get(cl, None)
        if not related:
            continue
        for model, model_admin_list in related.items():
            tool_url = _get_url_for_model(model)
            tools_url.append(tool_url)
            for model_admin in model_admin_list:
                tools_admin_site.append({'tool_name': model_admin.tool_name,
                            'tool_label': getattr(model_admin, 'tool_label', model_admin.model._meta.verbose_name_plural),
                            'tool_url': getattr(model_admin, 'tool_name', model_admin.model._meta.module_name),
                            'selected': False,
                            })
    if tools_admin_site:
        tools += tools_admin_site

    return tools


def _get_object_tools_in_route(route):
    base_url = urlresolvers.reverse('admin:index')
    res = []
    for item in route:
        obj = item['obj']
        if not obj:
            continue
        model_admin = item['admin']
        tool_name = item['tool_name']
        obj_tool = {'base_object': obj,
                    'base_object_opts': obj and obj._meta or None,
                    'tools': _smart_relations_object_tool_admin_site(
                                        item['site'],
                                        item['admin'],
                                        item['obj'],
                                        item['tool_name'],
                                   ),
                   }
        base_url += '%s/%s/' % (model_admin.model._meta.app_label, model_admin.model._meta.module_name)
        if tool_name:
            # Thereis a next model_admin and an object for this model_admin
            base_url += '%s/' % (obj.id)
            obj_tool['base_url'] = base_url
            base_url += '%s/' % tool_name
        if obj_tool['tools']:
            res.append(obj_tool)
    return res


def smart_relations_object_tool(context):
    route = _calculate_route(context, True) or []
    obj_tools = _get_object_tools_in_route(route)
    return {'obj_tools': obj_tools}
smart_relations_object_tool = register.inclusion_tag('admin/smart_relations_object_tool.html', takes_context=True)(smart_relations_object_tool)
