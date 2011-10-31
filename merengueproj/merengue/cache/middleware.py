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
from django.middleware.cache import FetchFromCacheMiddleware, UpdateCacheMiddleware


class CheckMemoizeCaches(object):

    def process_request(self, request):
        if not request.get_full_path().startswith(settings.MEDIA_URL):
            from merengue.cache import reload_memoize_caches
            reload_memoize_caches()
        return None


class UpdateAnonymousCacheMiddleware(UpdateCacheMiddleware):

    def __init__(self):
        super(UpdateAnonymousCacheMiddleware, self).__init__()

    def process_response(self, request, response):
        if getattr(settings, 'CACHE_SITE_FOR_ANONYMOUS', False):
            return super(UpdateAnonymousCacheMiddleware, self).process_response(request, response)
        else:
            return response


class FetchFromAnonymousCacheMiddleware(FetchFromCacheMiddleware):

    def __init__(self):
        super(FetchFromAnonymousCacheMiddleware, self).__init__()

    def process_request(self, request):
        if getattr(settings, 'CACHE_SITE_FOR_ANONYMOUS', False):
            return super(FetchFromAnonymousCacheMiddleware, self).process_request(request)
        else:
            return None
