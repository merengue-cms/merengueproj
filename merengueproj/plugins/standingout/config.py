from merengue.plugin import Plugin

from plugins.standingout.models import StandingOut
from plugins.standingout.admin import StandingOutAdmin


class PluginConfig(Plugin):
    name = 'Standing out'
    description = 'Standing out plugin'
    version = '0.0.1a'

    @classmethod
    def get_blocks(cls):
        return []

    @classmethod
    def section_models(cls):
        return []

    @classmethod
    def get_model_admins(cls):
        return [(StandingOut, StandingOutAdmin)]
