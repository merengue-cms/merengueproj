from django.utils.translation import ugettext_lazy as _

from merengue.plugins import Plugin
from merengue.registry import params
from merengue.section.admin import DocumentRelatedModelAdmin
from merengue.section.models import Document

from plugins.core.blocks import CoreMenuBlock, NavigationBlock, PrimaryLinksBlock, SecondaryLinksBlock


class PluginConfig(Plugin):
    name = 'Core'
    description = 'Core plugin'
    version = '0.0.1a'

    url_prefixes = (
    )

    config_params = [
        params.Single(name='home_initial_content',
                      label=_('home initial content'), default='1')
    ]


    @classmethod
    def get_blocks(cls):
        return [CoreMenuBlock, NavigationBlock, PrimaryLinksBlock, SecondaryLinksBlock]

    @classmethod
    def section_models(cls):
        # section_models of merengue core
        return [(Document, DocumentRelatedModelAdmin)]
