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

from django.conf import settings

from merengue.registry import params


class AjaxListParam(params.List):

    def render(self, name, widget_attrs,
               template_name='addthis/ajax_list_params.html',
               extra_context=None):
        # This extra check is needed in order to check if the plugin
        # is actually installed, to try or not to try to render
        # the template.
        if 'plugins.addthis' in settings.INSTALLED_APPS:
            return super(AjaxListParam, self).render(name, widget_attrs,
                                                     template_name,
                                                     extra_context)
        else:
            return ''
