from merengue.pluggable import Plugin
#from merengue.section.admin import DocumentRelatedModelAdmin
#from merengue.section.models import Document

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

    #@classmethod
    #def section_models(cls):
        ## section_models of merengue core
        #return [(Document, DocumentRelatedModelAdmin)]

    @classmethod
    def get_model_admins(cls):
        return [(Chunk, ChunkAdmin)]
