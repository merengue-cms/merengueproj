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

from django.db.models import Q

from merengue.registry.managers import RegisteredItemManager, RegisteredItemQuerySet


class BlockQuerySet(RegisteredItemQuerySet):

    def _clone(self, klass=None, setup=False, **kwargs):
        kwargs.update({'_place': getattr(self, '_place', None),
                       '_content': getattr(self, '_content', None)})
        return super(BlockQuerySet, self)._clone(klass, setup, **kwargs)

    def placed_in(self, place=None):
        # note: this method does not returns a real queryset
        self._place = place
        if place:
            return self.filter(placed_at=place)
        else:
            return self.all()

    def excluders(self, place, content):
        """ blocks which blocks excludes other blocks in one place """
        if content:
            return self.filter(placed_at=place, content__isnull=False, content__id=content.id).filter(Q(overwrite_if_place=True) | Q(overwrite_always=True))
        else:
            return self.filter(placed_at=place, content__isnull=False).filter(Q(overwrite_if_place=True) | Q(overwrite_always=True))

    def with_content(self, content):
        self._content = content
        if content:
            return self.filter(Q(content__isnull=True) | Q(content__id=content.id))
        else:
            return self.filter(content__isnull=True)

    def exclude_overrided(self, content=None):
        if content is None:
            content = getattr(self, '_content', None)
        if content is None:
            return self
        place = getattr(self, '_place', None)
        excluders = self.model.objects.actives().excluders(place, content)
        if excluders.count():
            query = Q(overwrite_always=True) | Q(id__in=excluders)
            excl_query = Q()
            for excl in excluders:
                excl_query = excl_query | Q(module=excl.module, class_name=excl.class_name)
            query = query | ~excl_query
            return self.filter(query)
        else:
            return self


class BlockManager(RegisteredItemManager):
    """ Block manager """

    def get_query_set(self):
        return BlockQuerySet(self.model)
