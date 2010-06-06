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

    @classmethod
    def get_blocks(cls):
        return [ChunksBlock]

    @classmethod
    def get_model_admins(cls):
        return [(Chunk, ChunkAdmin)]
