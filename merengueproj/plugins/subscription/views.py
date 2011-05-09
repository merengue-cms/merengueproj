# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from cmsutils.log import send_info
from merengue.base.models import BaseContent
from merengue.cache import invalidate_cache_for_path


def subscription_form(request, basecontent_id):
    content = BaseContent.objects.get(id=basecontent_id)
    subscribable = content.subscribable_set.actives()
    if not subscribable:
        return HttpResponseRedirect(content.get_absolute_url())
    subscribable = subscribable[0]
    app_label, module_name = subscribable.class_name.split('.')
    content_type = ContentType.objects.get(app_label=app_label, model=module_name)
    model_class = content_type.model_class()
    data = None
    if request.POST:
        data = request.POST
    form = model_class.class_form()(data)
    if form.is_valid():
        subscription = form.save(commit=False)
        subscription.subscribable = subscribable
        subscription.save()
        subscriber_listing_url = reverse('subscriber_listing', args=(basecontent_id, ))
        send_info(
            request,
            _('Request send successfully. See <a href="%(subscriber_listing)s">suscriber list</a>') % {
                'subscriber_listing': subscriber_listing_url,
            },
        )
        url_redirect = content.get_absolute_url()
        invalidate_cache_for_path(url_redirect)
        return HttpResponseRedirect(url_redirect)
    return render_to_response('subscription/subscription_form.html',
                              {'form': form,
                               'content': content,
                              },
                              context_instance=RequestContext(request))


def subscriber_listing(request, basecontent_id):
    content = BaseContent.objects.get(id=basecontent_id)
    subscribable = content.subscribable_set.actives()
    if not subscribable:
        return HttpResponseRedirect(content.get_absolute_url())
    subscribers = subscribable[0].basesubscription_set.all().order_by('last_name', 'first_name')
    return render_to_response('subscription/subscriber_listing.html',
                              {'subscribers': subscribers, 'content': content},
                              context_instance=RequestContext(request))
