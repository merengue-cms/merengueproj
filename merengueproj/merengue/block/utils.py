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

from merengue.cache import MemoizeCache, memoize

# block cache stuff  --------------------

_blocks_lookup_cache = MemoizeCache('displayed_blocks_cache')


# public functions   --------------------

def get_blocks_to_display(place=None, content=None):
    """
    Gets content related blocks excluding the ones overwritten by blocks within the same content
    """
    from merengue.block.models import RegisteredBlock
    return RegisteredBlock.objects.actives().placed_in(place).with_content(content).exclude_overrided()


def _get_all_blocks_to_display(place=None, content=None, section=None):
    """
    Three block groups are fetched separately in increasing priority:
        - site blocks (no content)
        - section related blocks
        - content related blocks
    """
    blocks = get_blocks_to_display(place, content)
    section_blocks = []
    if section:
        section_blocks = get_blocks_to_display(place, section).exclude_overrided(content)
    all_blocks = blocks + section_blocks
    sorted(all_blocks, key=lambda b: b.order)
    return all_blocks

get_all_blocks_to_display = memoize(_get_all_blocks_to_display, _blocks_lookup_cache, 3)


def clear_lookup_cache():
    global _blocks_lookup_cache
    _blocks_lookup_cache.clear()
