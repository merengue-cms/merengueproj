from merengue.plugins import Plugin
from merengue.section.admin import DocumentRelatedModelAdmin
from merengue.section.models import Document

from plugins.core.blocks import CoreMenuBlock, NavigationBlock, PrimaryLinksBlock, SecondaryLinksBlock


class PluginConfig(Plugin):
    name = 'Core'
    description = 'Core plugin'
    version = '0.0.1a'

    url_prefixes = (
    )

    @classmethod
    def get_blocks(cls):
        return [CoreMenuBlock, NavigationBlock, PrimaryLinksBlock, SecondaryLinksBlock]

    @classmethod
    def section_models(cls):
        # section_models of merengue core
        return [(Document, DocumentRelatedModelAdmin)]
