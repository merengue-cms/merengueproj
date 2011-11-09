from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from cmsutils.log import send_info
from merengue.perms.forms import AccessRequestForm


def access_request(request, exception=None, base_template='base.html'):
    data = None
    admin_index = reverse('admin_index')
    is_admin = request.get_full_path().startswith(admin_index)
    if request.method == 'GET' and not exception:
        return HttpResponseRedirect(settings.ACCESS_REQUEST_REDIRECT)
    elif request.method == 'POST':
        data = request.POST
        is_admin = is_admin or request.POST.get('url', '').startswith(admin_index)
    form = AccessRequestForm(request=request,
                             data=data,
                             exception=exception)
    if is_admin:
        base_template = 'admin/base.html'

    if form.is_valid():
        form.save()
        send_info(request, _('Access request successfully'))
        return HttpResponseRedirect(settings.ACCESS_REQUEST_REDIRECT)
    return render_to_response('perms/access_request.html',
                              {'form': form,
                               'base_template': base_template},
                              context_instance=RequestContext(request))
