from django.shortcuts import render_to_response
from django.template import RequestContext
from plugins.core.config import PluginConfig as CoreConfig
from merengue.base.models import BaseContent


def index(request):
    """ Index page """
    # put here your staff
    core_config = CoreConfig()
    main_content_index = int(core_config.get_config()['home_initial_content'].get_value())
    content = BaseContent.objects.get(pk=main_content_index)
    return render_to_response('website/index.html',
                              {'content': content},
                              context_instance=RequestContext(request))
