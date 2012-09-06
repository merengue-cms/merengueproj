from merengue.pluggable import Plugin

from plugins.custommeta.admin import CustomMetaAdmin
from plugins.custommeta.models import CustomMeta


class PluginConfig(Plugin):
    name = 'CustomMeta'
    description = 'CustomMeta plugin'
    version = '0.0.1a'
    model_admins = [(CustomMeta, CustomMetaAdmin)]

    def get_model_admins(self):
        return self.model_admins

    def models(self):
        return self.model_admins
