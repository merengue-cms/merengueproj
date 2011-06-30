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
from django.utils.functional import wraps


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


class MemoizeCache(object):
    """
    A cache class to be used with merengue.cache.memoize

    It allows you to memoize functions using Django caching system.

    Example::

        _cache = MemoizeCache('cache_prefix')

        def _heavyfunction(arg1, arg2):
            ... # a long process
        heavyfunction = memoize(_heavyfunction, _cache, 2)
    """

    def __init__(self, cache_prefix):
        self.cache_prefix = cache_prefix
        self._cache = cache.get(cache_prefix)
        if self._cache is None:
            self._cache = {}

    def __contains__(self, name):
        return name in self._cache

    def __getitem__(self, key):
        return self._cache.get(key)

    def __setitem__(self, key, value):
        self._cache[key] = value
        cache.set(self.cache_prefix, self._cache)

    def clear(self):
        self._cache = {}
        cache.set(self.cache_prefix, self._cache)


def memoize(func, cache, num_args, offset=0, convert_args_func=None):
    """
    It's like django.utils.functional.memoize but with an extra offset parameter

    Only the first num_args are considered when creating the key, but starting
    from offset.
    """
    def wrapper(*args):
        mem_args = args[offset:num_args]
        if convert_args_func is not None:
            mem_args = convert_args_func(mem_args)
        if mem_args in cache:
            return cache[mem_args]
        result = func(*args)
        cache[mem_args] = result
        return result
    return wraps(func)(wrapper)
