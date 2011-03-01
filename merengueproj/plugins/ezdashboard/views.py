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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from plugins.ezdashboard import catalog
from merengue.pluggable.utils import get_plugin


def dashboard(request):
    plugin_config = get_plugin('ezdashboard').get_config()
    return render_to_response('ezdashboard/dashboard.html',
                              {'plugin_config': plugin_config},
                              context_instance=RequestContext(request))


def gadgets_list(request):
    """ Returns a list of all gadget URLs """
    gadgets_url = []
    for name, Gadget in catalog.get_list():
        gadget = Gadget(request)
        gadgets_url.append(gadget.meta_url())
    return HttpResponse('\n'.join(gadgets_url), content_type='text/plain')


def gadget_meta(request, gadget_name):
    """ Returns an XML with gadget meta description """
    Gadget = catalog.get_by_name(gadget_name)
    gadget = Gadget(request)
    return HttpResponse(gadget.meta(), content_type='text/xml')


def gadget_view(request, gadget_name):
    """ Returns gadget HTML content """
    Gadget = catalog.get_by_name(gadget_name)
    gadget = Gadget(request)
    return HttpResponse(gadget.content())
