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

from django.db import models
from django.db.models.query import QuerySet


class RoleQuerySet(QuerySet):
    pass


class RoleManager(models.Manager):
    """ Registered item manager """

    def get_query_set(self):
        return RoleQuerySet(self.model)

    def without_anonymoususer(self):
        from merengue.perms import ANONYMOUS_ROLE_SLUG
        return self.get_query_set().exclude(slug=ANONYMOUS_ROLE_SLUG)
