# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.template import RequestContext
from django.template.loader import render_to_string


class StatusCodeMiddleware(object):
    """This middleware autodiscovers the current section from the url"""

    def process_response(self, request, response):
        if getattr(settings, 'HTTP_ERRORS_DEBUG', settings.DEBUG):
            return response

        template = settings.CATCH_STATUS_CODE.get(response.status_code, None)
        if not template:
            return response
        content = render_to_string(template, {}, context_instance=RequestContext(request))
        response._headers['content-type'] = ('Content-Type', 'text/html; charset=utf-8')
        response.content = content
        return response
