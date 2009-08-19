from pluginregistry.models import RegisteredPlugin
from registry.items import RegistrableItem


class Plugin(RegistrableItem):
    model = RegisteredPlugin

    @classmethod
    def get_category(cls):
        return 'plugin'

    @classmethod
    def get_actions(cls):
        return [] # to override in plugins
