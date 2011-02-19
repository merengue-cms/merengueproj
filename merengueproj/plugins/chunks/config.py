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

from merengue.pluggable import Plugin

from plugins.chunks.blocks import ChunksBlock
from plugins.chunks.models import Chunk
from plugins.chunks.admin import ChunkAdmin


class PluginConfig(Plugin):
    name = 'Chunks'
    description = 'Chunks plugin'
    version = '0.0.1a'

    url_prefixes = (
    )

    def get_blocks(self):
        return [ChunksBlock]

    def get_model_admins(self):
        return [(Chunk, ChunkAdmin)]
