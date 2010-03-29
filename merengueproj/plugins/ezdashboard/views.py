from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from plugins.ezdashboard import catalog
from plugins.ezdashboard.config import PluginConfig


def dashboard(request):
    plugin_config = PluginConfig.get_config()
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
