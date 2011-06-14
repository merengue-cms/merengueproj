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

from django.db.models import Manager, Q
from django.db.models.query import QuerySet

from merengue.perms.utils import get_roles


class PortalLinksQuerySet(QuerySet):

    def visible_by_user(self, user):
        queryset = self.all()
        if not user.is_superuser:
            queryset = queryset.filter(
                Q(visible_by_roles__isnull=True) | Q(visible_by_roles__in=get_roles(user)),
            ).distinct()
        return queryset


class PortalLinksManager(Manager):

    def get_query_set(self):
        return PortalLinksQuerySet(self.model)
