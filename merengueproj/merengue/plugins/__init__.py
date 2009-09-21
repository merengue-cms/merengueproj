from django.conf import settings
from django.db.models.signals import post_syncdb

from merengue.plugins import models as plugin_models
from merengue.plugins.models import RegisteredPlugin
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

    @classmethod
    def post_actions(cls):
        pass

    @classmethod
    def section_models(cls):
        return [] # to override in plugins


def active_default_plugins(*args, **kwargs):
    if kwargs['sender'] == plugin_models:
        from merengue.plugins.checker import register_plugin
        interactive = kwargs.get('interactive', None)
        if interactive:
            for plugin_dir in settings.ACTIVED_DEFAULTS_PLUGINS:
                plugin = register_plugin(plugin_dir)
                plugin.installed = True
                plugin.active = True
                plugin.save()

post_syncdb.connect(active_default_plugins)
