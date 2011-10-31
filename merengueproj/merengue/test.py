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
from django.test.simple import run_tests as django_run_tests
from johnny import cache


def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    # Disable Johnny cache backend because it does weird things. See #852
    query_cache_backend = cache.get_backend()
    query_cache_backend.unpatch()
    query_cache_backend.flush_query_cache()
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

    return django_run_tests(test_labels, verbosity, interactive, extra_tests)
