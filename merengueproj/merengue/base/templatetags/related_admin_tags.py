# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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


def _calculate_route(context):
    model_admin = context.get('model_admin', None)
    if model_admin:
        admin_site = model_admin.admin_site
        original = context.get('original', None) or context.get('object', None)
        site_list = [{'site': admin_site,
                    'opts': model_admin.opts,
                    'obj': original,
                    'admin': model_admin,
                    'tool_name': None,
                    }]
        next = admin_site.base_tools_model_admins.get(getattr(model_admin, 'tool_name', None), None)
        prev = model_admin
        while next:
            object_id = admin_site.base_object_ids.get(getattr(prev, 'tool_name', None), None)
            site_list += [{'site': next.admin_site,
                        'opts': next.opts,
                        'admin': next,
                        'obj': next._get_base_content(context.get('request'), object_id, next),
                        'tool_name': getattr(prev, 'tool_name', None),
                        }]
            prev = next
            next = admin_site.base_tools_model_admins.get(getattr(prev, 'tool_name', None), None)
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
                url_list += [{'label': _('Plugin administration'),
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
                            'url': urlresolvers.reverse('admin:%s_%s_change' % (route[0]['opts'].app_label, route[0]['opts'].module_name), args=(route[0]['obj'].id, )),
                            }]
            elif add:
                url_list += [{'label': _('Add'),
                            'url': urlresolvers.reverse('admin:%s_%s_add' % (route[0]['opts'].app_label, route[0]['opts'].module_name)),
                            }]
            base_url = url_list[-1]['url']

            for r in route[1:]:
                model_admin = r['admin']
                if not model_admin.one_to_one:
                    # in one to one related models, we hide listings
                    url_list += [{'label': _(r['site'].tool_label),
                                'url': base_url + r['site'].name + '/' + r['opts'].app_label + '/' + r['opts'].module_name + '/',
                                }]
                if r['obj']:
                    url_list += [{'label': r['obj'],
                                'url': base_url + r['site'].name + '/' + r['opts'].app_label + '/' + r['opts'].module_name + '/' + str(r['obj'].id) + '/',
                                }]
                elif add:
                    url_list += [{'label': _('Add'),
                                'url': base_url + r['site'].name + '/' + r['opts'].app_label + '/' + r['opts'].module_name + '/add/',
                                }]
                base_url = url_list[-1]['url']
        except NoReverseMatch:
            pass
    return {'url_list': url_list,
           }
advanced_breadcrumbs = register.inclusion_tag('admin/advanced_breadcrumbs.html', takes_context=True)(advanced_breadcrumbs)


def _get_url_for_model_admin(model_admin):
    return '%s/%s/' % (model_admin.model._meta.app_label, model_admin.model._meta.module_name)


def _smart_relations_object_tool_admin_site(admin_site, model_admin, obj, tool_name, tools=None, tools_url=None):
    tools = tools or []
    tools_admin_site = []
    tools_url = tools_url or []
    related_admin_sites = admin_site.related_admin_sites

    for related_admin_site__keys, related_admin_site__values in related_admin_sites.items():
        if isinstance(obj, related_admin_site__keys):
            for related_tool_name, related_admin_site in related_admin_site__values.items():
                model, tool_model_admin = related_admin_site._registry.items()[0]
                tool_url = _get_url_for_model_admin(tool_model_admin)
                tools_url.append(tool_url)
                tools_admin_site.append({'tool_name': related_tool_name,
                            'tool_label': related_admin_site.tool_label,
                            'tool_url': '%s/%s' % (related_tool_name, tool_url),
                            'selected': tool_name == related_tool_name,
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
    route = _calculate_route(context) or []
    route = route[-1:]
    obj_tools = _get_object_tools_in_route(route)
    return {'obj_tools': obj_tools}
smart_relations_object_tool = register.inclusion_tag('admin/smart_relations_object_tool.html', takes_context=True)(smart_relations_object_tool)
