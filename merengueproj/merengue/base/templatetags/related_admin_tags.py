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
                 }]
    next = admin_site.base_model_admin
    prev = model_admin
    while next:
        site_list += [{'site': next.admin_site,
                       'opts': next.opts,
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
        url_list += [{'label': _(r['site'].name.title()),
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
