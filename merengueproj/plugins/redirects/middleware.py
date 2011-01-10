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

from plugins.redirects.models import Redirect
from django import http
from django.conf import settings
from django.shortcuts import redirect


class RedirectMiddleware(object):
    """
    Redirect Plugin. Redirect if 404 is returned. Only active redirects.
    """

    def process_response(self, request, response):
        """
        Check if redirect_obj is needed.
        """

        if response.status_code != 404:
            # No need to check for a redirect_obj for non-404 responses.
            return response
        path = request.get_full_path()
        try:
            redirect_obj = Redirect.objects.get(old_path=path, is_active=True)
        except Redirect.DoesNotExist:
            redirect_obj = None
        if redirect_obj is None and settings.APPEND_SLASH:
            # Try removing the trailing slash.
            try:
                old_path = path[:path.rfind('/')] + path[path.rfind('/') + 1:]
                redirect_obj = Redirect.objects.get(old_path=old_path,
                                                                is_active=True)
            except Redirect.DoesNotExist:
                pass
        if redirect_obj is not None:
            if redirect_obj.new_path == '':
                return http.HttpResponseGone()
            return redirect(redirect_obj.new_path,
                                        permanent=redirect_obj.is_permanent)
        # No redirect_obj was found. Return the response.
        return response
