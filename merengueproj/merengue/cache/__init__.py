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
from django.db.models.query import QuerySet
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
        self.cache_version_key = '%s_version' % cache_prefix
        self._cache = cache.get(cache_prefix)
        if self._cache is None:
            self._cache = {}
        self._cache_version = cache.get(self.cache_version_key)
        if self._cache_version is None:
            self._cache_version = 1
            cache.get(self.cache_version_key, self._cache_version)

    def __contains__(self, name):
        return name in self._cache

    def __getitem__(self, key):
        return self._cache.get(key)

    def __setitem__(self, key, value):
        if isinstance(value, QuerySet):
            # force the queryset evaluation for avoiding a deadlock. See #2152
            len(value)
        self._cache[key] = value
        cache.set(self.cache_prefix, self._cache)
        self._incr_cache_version()

    def _incr_cache_version(self):
        self._cache_version += 1
        cache.set(self.cache_version_key, self._cache_version)

    def reload_if_dirty(self):
        if cache.get(self.cache_version_key) != self._cache_version:
            self._cache = cache.get(self.cache_prefix)
            if self._cache is None:
                self._cache = {}

    def clear(self):
        self._cache = {}
        cache.set(self.cache_prefix, self._cache)
        self._incr_cache_version()


def memoize(func, cache, num_args, offset=0, convert_args_func=None, update_cache_if_empty=True):
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
        if update_cache_if_empty or result:
            cache[mem_args] = result
        return result
    return wraps(func)(wrapper)


def reload_memoize_caches():
    from merengue.registry.managers import _registry_lookup_cache
    from merengue.block.utils import _blocks_lookup_cache
    from merengue.perms.utils import _roles_cache
    from merengue.section.models import _menu_sections_cache
    _registry_lookup_cache.reload_if_dirty()
    _blocks_lookup_cache.reload_if_dirty()
    _roles_cache.reload_if_dirty()
    _menu_sections_cache.reload_if_dirty()
