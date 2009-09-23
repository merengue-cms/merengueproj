from django import template
from django.core import urlresolvers
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext as _

from merengue.base.adminsite import RelatedAdminSite

register = template.Library()


def _calculate_route(context):
    opts = context.get('opts', None)
    model_admin = context.get('model_admin', None)
    if model_admin:
        admin_site = model_admin.admin_site
        original = context.get('original', None) or context.get('object', None)
        site_list = [{'site': admin_site,
                    'opts': model_admin.opts,
                    'obj': original,
                    'admin': model_admin,
                    }]
        _calculate_route_subadminsite(context, admin_site, model_admin, site_list)
        site_list.reverse()
        return site_list
    return None


def _calculate_route_subadminsite(context, admin_site, model_admin, site_list):
    try:
        next = _get_base_model_admin(admin_site)
    except IndexError:
        return
    prev = model_admin
    while next:
        site_list += [{'site': next.admin_site,
                    'opts': next.opts,
                    'admin': next,
                    'obj': _get_obj(context, prev, site_list),
                    }]

        prev = next
        if next and next.admin_site:
            _calculate_route_subadminsite(context, next.admin_site, next, site_list)
        next = getattr(next, 'base_model_admin', None)


def _get_base_model_admin(admin_site):
    return getattr(admin_site, 'base_model_admin', admin_site.base_model_admins.values()[0])


def _get_obj(context, model_admin, site_list):
    related_field = getattr(model_admin, 'related_field', None)
    if related_field:
        obj = getattr(model_admin, related_field, None)
        if obj:
            return obj
        try:
            obj = model_admin._get_base_content(context['request'])
        except AttributeError:
            pass
        if obj:
            return obj
        try:
            related_obj = site_list[-1]['obj']
            obj = getattr(related_obj, related_field, None)
            if obj:
                return obj
            obj = getattr(related_obj, "%s_set" % related_field, None)
            if obj:
                return obj.all()[0]
        except IndexError:
            pass
    return None


def advanced_breadcrumbs(context):
    add = context.get('add', None)
    change = context.get('change', None)
    route = _calculate_route(context)
    url_list = []

    if route:
        try:
            url_list = [{'label': _('Home'),
                        'url': urlresolvers.reverse('admin:index'),
                        },
                        {'label': _(route[0]['opts'].app_label.title()),
                        'url': urlresolvers.reverse('admin:app_list', args=(route[0]['opts'].app_label, )),
                        },
                        {'label': _(route[0]['opts'].verbose_name_plural.title()),
                        'url': urlresolvers.reverse('admin:%s_%s_changelist' % (route[0]['opts'].app_label, route[0]['opts'].module_name)),
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


def _get_url_related_admin_site(context, admin_site, model_admin_next, obj):
    is_add_view = context.get('add', None)
    is_change_view = context.get('change', None)
    original = context.get('original', None)
    tool_name = model_admin_next.tool_name or model_admin_next.model._meta.module_name
    model_admin_url = ''
    if original == obj:
        if is_change_view:
            model_admin_url = '%s/%s/%s/' %(tool_name, model_admin_next.model._meta.app_label, model_admin_next.model._meta.module_name)
    else:
        if not is_add_view and not is_change_view:
            model_admin_url = '../../../%s/%s/%s/' %(tool_name, model_admin_next.model._meta.app_label, model_admin_next.model._meta.module_name)
        if is_change_view:
            model_admin_url = '../../../../%s/%s/%s/' %(tool_name, model_admin_next.model._meta.app_label, model_admin_next.model._meta.module_name)
    return model_admin_url


def _smart_relations_object_tool_admin_site(context, admin_site, model_admin, obj, tools=None, tools_url=None):
    tools = tools or []
    tools_admin_site = []
    tools_url = tools_url or []
    related_admin_sites = admin_site.related_admin_sites

    for related_admin_site__keys, related_admin_site__values in related_admin_sites.items():
        if isinstance(obj, related_admin_site__keys):
            for tool_name, related_admin_site in related_admin_site__values.items():
                model, tool_model_admin = related_admin_site._registry.items()[0]
                tool_url = _get_url_related_admin_site(context, related_admin_site, tool_model_admin, obj)
                if not tool_url in tools_url:
                    tools_url.append(tool_url)
                    tools_admin_site.append({'tool_name': tool_name,
                                'tool_label': related_admin_site.tool_label,
                                'tool_url': tool_url,
                                'selected': context.get('model_admin', None) == tool_model_admin,
                                })
    if tools_admin_site:
        tools.append(tools_admin_site)


    if isinstance(admin_site, RelatedAdminSite):
        model_admin_next = _get_base_model_admin(admin_site)
        return _smart_relations_object_tool_admin_site(context, model_admin_next.admin_site, model_admin_next, obj, tools, tools_url)
    return tools


def smart_relations_object_tool(context, obj, obj_related=None):
    original = obj
    model_admin = context.get('model_admin', None)
    request = context.get('request')
    model_admin = context.get('model_admin', None)
    admin_site = model_admin.admin_site
    tools = _smart_relations_object_tool_admin_site(context, admin_site, model_admin, obj)
    return {'tools': tools}
smart_relations_object_tool = register.inclusion_tag('admin/smart_relations_object_tool.html', takes_context=True)(smart_relations_object_tool)
