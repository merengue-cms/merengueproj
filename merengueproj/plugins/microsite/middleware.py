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
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect

from merengue.middleware import HttpStatusCode403Provider
from merengue.urlresolvers import get_url_default_lang


class MicrositeMiddleware(HttpStatusCode403Provider):
    """This middleware autodiscovers the current section from the url"""

    def process_request(self, request):
        path_info = request.get_full_path()
        url_args = [item for item in path_info.split('/') if item]
        from plugins.microsite.config import PluginConfig
        url_prefixes = PluginConfig.url_prefixes[0][0]
        prefix_microsite = url_prefixes.get(get_url_default_lang(), 'en')
        if len(url_args) > 1 and url_args[0] == prefix_microsite:
            del url_args[0]
            url_new = '/'.join(url_args)
            url_new = '/%s/' % url_new
            return HttpResponseRedirect(url_new)

    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a section for non-404 responses.
        try:
            path_info = request.path_info
            url_args = [item for item in path_info.split('/') if item]
            return self.microsite_dispatcher(request, url_args)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except PermissionDenied, exception:
            return self.process_exception(request, exception)
        except:
            if settings.DEBUG:
                raise
            return response

    def microsite_dispatcher(self, request, url_args):
        from plugins.microsite.views import microsite_url, microsite_view, document_microsite_view
        from plugins.microsite.urls import PREFIX_DOC
        url_args_len = len(url_args)
        if url_args_len == 4 and url_args[1] == PREFIX_DOC:
            return document_microsite_view(request, url_args[0], url_args[2], url_args[3])
        if url_args_len == 1:
            return microsite_view(request, url_args[0])
        elif url_args_len > 1:
            return microsite_url(request, url_args[0], url_args[1:])
        raise Http404
