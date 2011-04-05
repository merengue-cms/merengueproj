from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins import customportlet
from plugins.customportlet.admin import CustomPortletAdmin
from plugins.customportlet.blocks import CustomPortletBlock
from plugins.customportlet.models import CustomPortlet


class PluginConfig(Plugin):
    name = 'Custom portlet'
    description = 'Custom portlet'
    version = '0.0.1a'

    config_params = [
        params.Single(name='limit', label=_('data limit of custom portlet'),
                      default=customportlet.MAX_BLOCKS_NUMBER),
    ]

    @classmethod
    def get_blocks(cls):
        return [CustomPortletBlock]

    @classmethod
    def get_model_admins(cls):
        return [(CustomPortlet, CustomPortletAdmin)]
