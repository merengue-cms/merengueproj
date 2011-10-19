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
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from merengue.perms import utils as perms_api
from merengue.section.views import section_view, content_section_view

from plugins.microsite.models import MicroSite


def microsite_view(request, microsite_slug):
    return section_view(request, microsite_slug)


def microsite_url(request, microsite_slug, url):
    microsite = get_object_or_404(MicroSite, slug=microsite_slug)
    perms_api.assert_has_permission(microsite, request.user, 'view')
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    urlresolvers.set_urlconf(urlconf)
    index_prefix = request.get_full_path().index(microsite_slug)
    prefix = request.get_full_path()[:index_prefix + len(microsite_slug) + 1]
    resolver = urlresolvers.RegexURLResolver(r'^%s' % prefix, urlconf)
    newurl = request.path_info
    try:
        callback, callback_args, callback_kwargs = resolver.resolve(
                            newurl)
    except urlresolvers.Resolver404, e:
        if settings.APPEND_SLASH and (not newurl.endswith('/')):
            newurl = newurl + '/'
            if settings.DEBUG and request.method == 'POST':
                raise RuntimeError((""
                    "You called this URL via POST, but the URL doesn't end "
                    "in a slash and you have APPEND_SLASH set. Django can't "
                    "redirect to the slash URL while maintaining POST data. "
                    "Change your form to point to %s (note the trailing "
                    "slash), or set APPEND_SLASH=False in your Django "
                    "settings.") % newurl)
            return HttpResponseRedirect(newurl)
        raise e
    if 'extra_context' in callback.func_code.co_varnames[:callback.func_code.co_argcount]:
        extra_context = {'section': microsite, 'microsite': microsite}
        callback_kwargs = callback_kwargs or {}
        extra_context_kwargs = callback_kwargs.get('extra_context', {})
        extra_context.update(extra_context_kwargs)
        callback_kwargs['extra_context'] = extra_context
    return callback(request, *callback_args, **callback_kwargs)


def document_microsite_view(request, microsite_slug, doc_id, doc_slug):
    return content_section_view(request, microsite_slug, doc_id, doc_slug)
