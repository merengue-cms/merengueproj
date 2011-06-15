from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string

from merengue.base.models import BaseContent
from plugins.core.forms import HotLinkForm


def hotlink(request, content_id):
    content = BaseContent.objects.get(pk=content_id).get_real_instance()
    data = None
    if request.method == 'POST':
        data = request.POST
    form = HotLinkForm(request.user, content, data=data)
    if form.is_valid():
        menu = form.save()
        return HttpResponseRedirect(menu.url)
    return HttpResponse(render_to_string('core/hotlink.html',
                        {'form': form,
                         'content': content}), mimetype='text/html')
