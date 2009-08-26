from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    """ Index page """
    # put here your staff
    return render_to_response('website/index.html',
                              {},
                              context_instance=RequestContext(request))
