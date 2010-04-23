from django.utils.translation import ugettext_lazy as _

from merengue.plugins import Plugin
from merengue.registry import params

from plugins.googlesearch.blocks import GoogleSearchBlock


class PluginConfig(Plugin):
    name = 'Google search'
    description = 'Google search plugin'
    version = '0.0.1a'

    config_params = [
        params.Single(name='custom_search_control', label=_('Custom search control'), default='003808332573069177904:wm3_yobt584'),
        params.Single(name='language', label=_('language'), default='es'),
    ]

    @classmethod
    def get_blocks(cls):
        return [GoogleSearchBlock]
