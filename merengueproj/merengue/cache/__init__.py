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
from django.utils.cache import _generate_cache_header_key


def invalidate_cache_for_path(request_path):
    """ invalidates cache based on request.path """

    # use a dummy request object so we can call django's _generate_cache_header_key
    class Request(object):

        def __init__(self, request_path):
            self.request_path = request_path

        def get_full_path(self):
            return self.request_path

    request = Request(request_path)
    cache_header_key = _generate_cache_header_key(settings.CACHE_MIDDLEWARE_KEY_PREFIX, request)

    # cache must be invalidated for all available languages
    if settings.USE_I18N:
        base_key = cache_header_key[:cache_header_key.rfind('.')]
        for code, name in settings.LANGUAGES:
            key = "%s.%s" % (base_key, code)
            cache.delete(key)
    else:
        cache.delete(cache_header_key)


def invalidate_johnny_cache(model, invalidate_parent=False, parent_finish=None):
    if 'johnny' in settings.INSTALLED_APPS:
        from johnny import cache
        query_cache_backend = cache.get_backend()
        query_cache_backend.patch()
        if parent_finish and not issubclass(model, parent_finish):
            return
        cache.invalidate(model._meta.db_table)
        if not invalidate_parent:
            return

        for model_parent in model.__bases__:
            if parent_finish and not issubclass(model, parent_finish):
                continue
            invalidate_johnny_cache(model_parent, invalidate_parent, parent_finish)
