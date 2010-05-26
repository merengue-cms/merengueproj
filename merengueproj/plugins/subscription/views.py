from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from cmsutils.log import send_info
from merengue.base.models import BaseContent
from merengue.base.utils import invalidate_cache_for_path


def subscription_form(request, basecontent_slug):
    content = BaseContent.objects.get(slug=basecontent_slug)
    subscribable = content.subscribable_set.actives()
    if not subscribable:
        return HttpResponseRedirect(content.get_absolute_url())
    subscribable = subscribable[0]
    app_label, module_name = subscribable.class_name.split('.')
    content_type = ContentType.objects.get(app_label=app_label, model= module_name)
    model_class = content_type.model_class()
    data = None
    if request.POST:
        data = request.POST
    form = model_class.class_form()(data)
    if form.is_valid():
        form.save()
        send_info(request, _('Request send successfully'))
        url_redirect = content.get_absolute_url()
        invalidate_cache_for_path(url_redirect)
        return HttpResponseRedirect(url_redirect)
    return render_to_response('subscription/subscription_form.html',
                              {'form': form,
                               'content': content,
                              },
                              context_instance=RequestContext(request))
