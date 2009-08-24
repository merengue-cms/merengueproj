from merengue.plug.models import RegisteredPlugin
from merengue.registry.items import RegistrableItem

PLUG_CACHE_KEY = 'plug__loaded'


class Plugin(RegistrableItem):
    model = RegisteredPlugin

    @classmethod
    def get_category(cls):
        return 'plugin'

    @classmethod
    def get_actions(cls):
        return [] # to override in plugins

    @classmethod
    def get_blocks(cls):
        return [] # to override in plugins
