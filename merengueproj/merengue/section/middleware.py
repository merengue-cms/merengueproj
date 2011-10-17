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
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import Http404

from merengue.middleware import HttpStatusCode403Provider

_section_prefixes = []


def register_section_prefix(section_prefix):
    if section_prefix not in _section_prefixes:
        _section_prefixes.append(section_prefix)


def unregister_section_prefix(section_prefix):
    if section_prefix in _section_prefixes:
        _section_prefixes.remove(section_prefix)


class RequestSectionMiddleware(object):
    """This middleware autodiscovers the current section from the url"""

    def process_request(self, request):
        from merengue.section.models import BaseSection

        section = None
        if request.path and not request.path.startswith(settings.MEDIA_URL):
            matched_prefix = None
            for section_prefix in _section_prefixes + ['/', ]:
                if request.path.startswith(section_prefix):
                    matched_prefix = section_prefix
                    break
            if matched_prefix:
                section_path = request.path[len(matched_prefix):]
                next_slash_index = section_path.find('/')
                section_slug = section_path[:next_slash_index]
                try:
                    cache_key = 'section_%s' % section_slug
                    section = cache.get(cache_key)
                    if section is None:
                        section = BaseSection.objects.get(slug=section_slug)
                        cache.set(cache_key, section)
                except:
                    # we put an blank except because some times in WSGI in a heavy loaded environments
                    # backends specific exceptions can be thrown, i.e. psycopg.ProgrammingError
                    pass
        request.section = section


class ResponseSectionMiddleware(HttpStatusCode403Provider):
    """This middleware autodiscovers the current section from the url"""

    def process_response(self, request, response):
        from merengue.section.views import section_dispatcher
        if response.status_code != 404:
            return response  # No need to check for a section for non-404 responses.
        try:
            return section_dispatcher(request, request.path_info)
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


class DebugSectionMiddleware(object):
    """This middleware checks for a GET parameter for a special debug mode"""

    def process_request(self, request):
        use_section_data = request.GET.get('use_section_data', False)
        if use_section_data:
            request.use_section_data = True
