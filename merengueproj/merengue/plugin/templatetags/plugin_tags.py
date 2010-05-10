from django.template import Library
from django.contrib.admin.templatetags.admin_list import (result_headers,
                                                          results)

register = Library()


def plugin_admin_result_list(cl):
    plugin_results = []
    for i, result in enumerate(list(results(cl))):
        item = cl.result_list[i]
        plugin_results.append(dict(result=result, broken=item.broken))
    return {'cl': cl,
            'result_headers': list(result_headers(cl)),
            'plugin_results': plugin_results}
plugin_admin_result_list = register.inclusion_tag("admin/plugin/change_list_results.html")(plugin_admin_result_list)
