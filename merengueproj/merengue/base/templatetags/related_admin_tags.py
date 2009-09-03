from django import template
from django.core import urlresolvers
from django.utils.translation import ugettext as _


register = template.Library()


def _calculate_route(context):
    opts = context.get('opts', None)
    model_admin = context.get('model_admin', None)
    admin_site = model_admin.admin_site
    original = context.get('original', None) or context.get('object', None)
    site_list = [{'site': admin_site,
                  'opts': model_admin.opts,
                  'obj': original,
                  'admin': model_admin,
                 }]
    next = admin_site.base_model_admin
    prev = model_admin
    while next:
        site_list += [{'site': next.admin_site,
                       'opts': next.opts,
                       'admin': next,
                       'obj': getattr(prev, 'basecontent', None),
                      }]
        prev = next
        next = getattr(next, 'base_model_admin', None)
    site_list.reverse()
    return site_list


def advanced_breadcrumbs(context):
    add = context.get('add', None)
    change = context.get('change', None)
    route = _calculate_route(context)
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

    return {'url_list': url_list,
           }
advanced_breadcrumbs = register.inclusion_tag('admin/advanced_breadcrumbs.html', takes_context=True)(advanced_breadcrumbs)


def smart_relations_object_tool(context):
    original = context.get('basecontent', None) or context.get('original', None)
    model_admin = context.get('model_admin', None)
    request = context.get('request')
    if not original:
        return {}
    from merengue.base.adminsite import site
    from django.template.defaultfilters import slugify
    tools = []
    base_url = urlresolvers.reverse('admin:%s_%s_change' % (original._meta.app_label, original._meta.module_name), args=(original.id, ))
    for key in site.related_admin_sites.keys():
        if isinstance(original, key):
            for tool_name, related_admin_site in site.related_admin_sites[key].items():
                model, tool_model_admin = related_admin_site._registry.items()[0]
                tool_url = '%s%s/%s/%s/' % (base_url, slugify(tool_name), model._meta.app_label, model._meta.module_name, )
                if tool_model_admin.one_to_one:
                    # link directly to change form or add form
                    qs = tool_model_admin.queryset(request, basecontent=original)
                    if qs:
                        obj = qs.get()
                        tool_url += str(obj.pk)
                    else:
                        tool_url += 'add/'
                tools.append({'tool_name': tool_name,
                              'tool_label': related_admin_site.tool_label,
                              'tool_url': tool_url,
                              'selected': model_admin == tool_model_admin,
                             })
    return {'tools': tools}
smart_relations_object_tool = register.inclusion_tag('admin/smart_relations_object_tool.html', takes_context=True)(smart_relations_object_tool)
