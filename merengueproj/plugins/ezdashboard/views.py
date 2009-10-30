from django.shortcuts import render_to_response
from django.template import RequestContext

from plugins.ezdashboard.config import PluginConfig


def dashboard(request):
    plugin_config = PluginConfig.get_config()
    return render_to_response('ezdashboard/dashboard.html',
                              {'plugin_config': plugin_config},
                              context_instance=RequestContext(request))
