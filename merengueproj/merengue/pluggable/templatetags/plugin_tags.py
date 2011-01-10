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
