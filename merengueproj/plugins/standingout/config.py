from merengue.pluggable import Plugin

from plugins.standingout.admin import StandingOutAdmin, StandingOutCategoryAdmin
from plugins.standingout.models import StandingOut, StandingOutCategory
from plugins.standingout.blocks import StandingOutBlock


class PluginConfig(Plugin):
    name = 'Standing out'
    description = 'Standing out plugin'
    version = '0.0.1a'

    @classmethod
    def get_blocks(cls):
        return [StandingOutBlock]

    @classmethod
    def section_models(cls):
        return []

    @classmethod
    def get_model_admins(cls):
        return [(StandingOut, StandingOutAdmin), (StandingOutCategory, StandingOutCategoryAdmin)]
