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

from django.shortcuts import render_to_response
from django.template import RequestContext
from merengue.pluggable.utils import get_plugin
from merengue.base.models import BaseContent


def index(request):
    """ Index page. You can override as you like """
    core_config = get_plugin('core').get_config()
    main_content_index = core_config['home_initial_content'].get_value()
    content = BaseContent.objects.get(pk=main_content_index).get_real_instance()
    return render_to_response([content._meta.content_view_template,
                               'website/index.html'],
                              {'content': content},
                              context_instance=RequestContext(request))
