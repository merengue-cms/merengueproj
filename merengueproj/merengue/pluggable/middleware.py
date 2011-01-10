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
from django.utils import translation

from merengue.pluggable.loading import load_plugins, plugins_loaded


class ActivePluginsMiddleware(object):
    """ Middleware that enable active plugins in every request """

    def process_request(self, request):
        if request.get_full_path().startswith(settings.MEDIA_URL):
            return None # plugin activation is not needed on static files
        if not plugins_loaded():
            load_plugins()
            # reset all i18n catalogs to load plugin ones
            if settings.USE_I18N:
                lang = translation.get_language()
                translation.trans_real._translations = {}
                translation.deactivate()
                translation.activate(lang)
        return None


class PluginMiddlewaresProxy(object):
    """ Middleware that calls to all plugins middlewares """

    def process_request(self, request):
        from merengue.pluggable.utils import get_plugins_middleware_methods
        for method in get_plugins_middleware_methods('request_middleware'):
            response = method(request)
            if response:
                return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        from merengue.pluggable.utils import get_plugins_middleware_methods
        for method in get_plugins_middleware_methods('view_middleware'):
            response = method(request, view_func, view_args, view_kwargs)
            if response:
                return response

    def process_response(self, request, response):
        from merengue.pluggable.utils import get_plugins_middleware_methods
        for method in get_plugins_middleware_methods('response_middleware'):
            response = method(request, response)
        return response

    def process_exception(self, request, exception):
        from merengue.pluggable.utils import get_plugins_middleware_methods
        for method in get_plugins_middleware_methods('exception_middleware'):
            response = method(request)
            if response:
                return response
