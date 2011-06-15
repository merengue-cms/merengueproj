from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string

from merengue.base.models import BaseContent
from plugins.core.forms import ExportContentForm


def export_content(request, content_id):
    content = BaseContent.objects.get(pk=content_id).get_real_instance()
    data = None
    if request.method == 'POST':
        data = request.POST
    form = ExportContentForm(request.user, content, data=data)
    if form.is_valid():
        menu = form.save()
        return HttpResponseRedirect(menu.url)
    return HttpResponse(render_to_string('core/export_content.html',
                        {'form': form,
                         'content': content}), mimetype='text/html')
