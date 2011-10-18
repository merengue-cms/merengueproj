from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from cmsutils.log import send_info
from merengue.perms.forms import AccessRequestForm


def access_request(request, exception=None):
    data = None
    if request.method == 'GET' and not exception:
        return HttpResponseRedirect(settings.ACCESS_REQUEST_REDIRECT)
    elif request.method == 'POST':
        data = request.POST
    form = AccessRequestForm(request=request,
                             data=data,
                             exception=exception)
    if form.is_valid():
        form.save()
        send_info(request, _('Access request successfully'))
        return HttpResponseRedirect(settings.ACCESS_REQUEST_REDIRECT)
    return render_to_response('perms/access_request.html', {'form': form},
                              context_instance=RequestContext(request))
