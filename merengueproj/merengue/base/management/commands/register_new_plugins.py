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

# -*- coding: utf-8 -*-
from merengue.base.management.base import MerengueCommand
from merengue.pluggable import register_all_plugins
from merengue.pluggable.models import RegisteredPlugin

from johnny import cache


class Command(MerengueCommand):
    help = "Register new plugins found in plugins directory"
    requires_model_validation = True

    def handle(self, **options):
        print 'Registering plugins...'
        register_all_plugins(verbose=True)
        # cache invalidation
        print 'Invalidating plugins cache...'
        query_cache_backend = cache.get_backend()
        query_cache_backend.patch()
        cache.invalidate(RegisteredPlugin._meta.db_table)
        print 'Done.'
