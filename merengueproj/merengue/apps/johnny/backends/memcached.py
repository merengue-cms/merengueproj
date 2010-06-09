#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Infinite caching memcached class.  Caches forever when passed a timeout
of 0. To use, change your ``CACHE_BACKEND`` setting to something like this::

    CACHE_BACKEND="johnny.backends.memcached://.."
"""

from django.conf import settings
from django.core.cache.backends import memcached
from django.utils.encoding import smart_str


class CacheClass(memcached.CacheClass):
    """By checking ``timeout is None`` rather than ``not timeout``, this
    cache class allows for non-expiring cache writes on certain backends,
    notably memcached."""

    def _get_key(self, key):
        return settings.SECRET_KEY + smart_str(key)

    def add(self, key, value, timeout=None):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if timeout is None:
            timeout = self.default_timeout
        return self._cache.add(self._get_key(key), value, timeout)

    def set(self, key, value, timeout=None):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if timeout is None:
            timeout = self.default_timeout
        self._cache.set(self._get_key(key), value, timeout)

    def get(self, key, default=None):
        return super(CacheClass, self).get(self._get_key(key), default)

    def delete(self, key):
        return super(CacheClass, self).delete(self._get_key(key))

    def get_many(self, keys):
        keys = [self._get_key(key) for key in keys]
        return super(CacheClass, self).get_many(keys)

    def incr(self, key, delta=1):
        return super(CacheClass, self).incr(self._get_key(key), delta)

    def decr(self, key, delta=1):
        return super(CacheClass, self).decr(self._get_key(key), delta)
