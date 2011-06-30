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

from cmsutils.utils import QuerySetWrapper

from merengue.registry.managers import RegisteredItemManager, RegisteredItemQuerySet


class FakeBlockQuerySet(QuerySetWrapper):

    def __init__(self, blocks, place, content=None):
        super(FakeBlockQuerySet, self).__init__(blocks)
        self.place = place
        self.content = content
        if not hasattr(self, 'model'):
            from merengue.block.models import RegisteredBlock
            self.model = RegisteredBlock

    def __add__(self, blocks):
        """ add a block removing duplicated elements (like and ordered set) """
        if isinstance(blocks, FakeBlockQuerySet):
            blocks = blocks.data
        blocks_to_add = [b for b in blocks if b not in self.data]
        return FakeBlockQuerySet(self.data + blocks_to_add, self.place, self.content)

    def _clone(self):
        return FakeBlockQuerySet(self.data, self.place, self.content)

    def _update(self, blocks):
        return FakeBlockQuerySet(blocks, self.place, self.content)

    def exclude_overrided(self, content=None):
        if content is None:
            content = self.content
        excluders = [b for b in self.model.objects.actives().excluders(self.place, content)]
        excluders_classes = ['%s.%s' % (b.module, b.class_name) for b in excluders]
        non_overrided_blocks = []
        for block in self:
            block_class = '%s.%s' % (block.module, block.class_name)
            if content is None or block.overwrite_always or \
               block in excluders or block_class not in excluders_classes:
                non_overrided_blocks.append(block)
        return self._update(non_overrided_blocks)

    def with_content(self, content):
        self.content = content
        if content:
            return self._update([b for b in self if b.content_id is None or b.content_id == content.id])
        else:
            return self._update([b for b in self if b.content_id is None])

    def get_items(self):
        for item in self:
            yield item.get_registry_item()


class BlockQuerySet(RegisteredItemQuerySet):

    def placed_in(self, place=None):
        # note: this method does not returns a real queryset
        blocks = self.all()
        if place is not None:
            blocks = [b for b in blocks if b.placed_at == place]
        return FakeBlockQuerySet(blocks, place)

    def excluders(self, place, content):
        """ blocks which blocks excludes other blocks in one place """
        return FakeBlockQuerySet(
            [b for b in self if b.content_id is not None and
               (content is None or b.content_id == content.id) and
               (b.placed_at == place and b.overwrite_if_place or b.overwrite_always)],
            place,
        )


class BlockManager(RegisteredItemManager):
    """ Block manager """

    def get_query_set(self):
        return BlockQuerySet(self.model)
