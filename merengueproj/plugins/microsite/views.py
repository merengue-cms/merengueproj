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

from django.conf import settings
from django.core import urlresolvers
from django.http import Http404
from django.shortcuts import get_object_or_404

from plugins.microsite.models import MicroSite


def microsite_view(request, microsite_slug):
    return microsite_url(request, microsite_slug)


def microsite_dispatcher(request):
    path_info = request.path_info
    url_args = [item for item in path_info.split('/') if item]
    if url_args:
        return microsite_url(request, url_args[0], url_args[1:])
    raise Http404


def microsite_url(request, microsite_slug, url):
    microsite = get_object_or_404(MicroSite, slug=microsite_slug)
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    urlresolvers.set_urlconf(urlconf)
    resolver = urlresolvers.RegexURLResolver(r'^/%s/' % microsite_slug, urlconf)
    callback, callback_args, callback_kwargs = resolver.resolve(
                        request.path_info)
    request.section = microsite
    if 'extra_context' in callback.func_code.co_varnames[:callback.func_code.co_argcount]:
        extra_context = {'section': microsite, 'microsite': microsite}
        callback_kwargs = callback_kwargs or {}
        extra_context_kwargs = callback_kwargs.get('extra_context', {})
        extra_context.update({'extra_context': extra_context_kwargs})
        callback_kwargs['extra_context'] = extra_context
    return callback(request, *callback_args, **callback_kwargs)
