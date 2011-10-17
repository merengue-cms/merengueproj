from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext


from merengue.perms.forms import AccessRequestForm


def access_request(request, exception=None):
    data = None
    if request.POST:
        data = request.POST
    form = AccessRequestForm(request=request,
                             data=data,
                             exception=exception)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/')
    return render_to_response('perms/access_request.html', {'form': form},
                              context_instance=RequestContext(request))
