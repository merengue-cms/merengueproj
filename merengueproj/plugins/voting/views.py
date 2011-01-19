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

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Template, RequestContext

from merengue.base.models import BaseContent

from plugins.voting.models import Vote

RATING_TEMPLATE = Template('{% load voting_tags %}{% voting obj %}')


def vote_object(request, object_id):
    if not request.user.is_authenticated():
        raise PermissionDenied()

    try:
        obj = BaseContent.objects.get(id=object_id)

        if request.method == 'POST':
            vote = int(request.POST['vote'])
            # TODO: use the request field that says where do we come from
            next = '/'
            Vote.objects.record_vote(obj, request.user, vote)

            is_ajax = request.POST.get('is_ajax', False)
            if is_ajax:
                context = RequestContext(request, {'user': request.user,
                                                   'obj': obj})
                return HttpResponse(RATING_TEMPLATE.render(context))
            else:
                if hasattr(obj, 'get_absolute_url'):
                    if callable(getattr(obj, 'get_absolute_url')):
                        next = obj.get_absolute_url()
                    else:
                        next = obj.get_absolute_url
                return HttpResponseRedirect(next)

    except ObjectDoesNotExist:
        raise Http404
