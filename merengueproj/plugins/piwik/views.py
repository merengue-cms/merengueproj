# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

from merengue.perms.decorators import permission_required
from merengue.pluggable.utils import get_plugin


@permission_required(codename='view_my_stats')
def index(request):
    piwik_url = get_plugin('piwik').get_config().get('url').get_value()
    return render_to_response('piwik/index.html',
                              {'piwik_url': piwik_url},
                              context_instance=RequestContext(request))


@permission_required(codename='view_all_stats')
def ranking(request):
    piwik_url = get_plugin('piwik').get_config().get('url').get_value()
    return render_to_response('piwik/ranking_stats.html',
                              {'piwik_url': piwik_url},
                              context_instance=RequestContext(request))


@permission_required(codename='view_my_stats')
def ranking_by_owner(request):
    piwik_url = get_plugin('piwik').get_config().get('url').get_value()
    return render_to_response('piwik/ranking_stats.html',
                              {'by_owner': True,
                               'piwik_url': piwik_url},
                              context_instance=RequestContext(request))
