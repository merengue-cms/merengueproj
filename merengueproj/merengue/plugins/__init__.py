from django.conf import settings
from django.db.models.signals import post_syncdb

from merengue.plugins import models as plugin_models
from merengue.plugins.models import RegisteredPlugin
from merengue.plugins.utils import get_plugin_config
from merengue.registry import register, is_registered
from merengue.registry.items import RegistrableItem

PLUG_CACHE_KEY = 'plug__loaded'


class Plugin(RegistrableItem):
    model = RegisteredPlugin
    url_prefixes = ()

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

    @classmethod
    def section_register_hook(cls, site_related, model):
        pass


def register_plugin(plugin_dir):
    plugin_config = get_plugin_config(plugin_dir)
    if plugin_config:
        if not is_registered(plugin_config):
            register(plugin_config)
        plugin = RegisteredPlugin.objects.get_by_item(plugin_config)
        plugin.name = getattr(plugin_config, 'name', plugin_dir)
        plugin.directory_name = plugin_dir
        plugin.description = getattr(plugin_config, 'description', '')
        plugin.version = getattr(plugin_config, 'version', '')
        plugin.required_apps = getattr(plugin_config, 'required_apps',
                                       None)
        plugin.required_plugins = getattr(plugin_config,
                                          'required_plugins',
                                          None)
        plugin.save()
        return plugin
    return None


def enable_active_plugins():
    from merengue.plugins.utils import enable_plugin, get_plugin_module_name
    for plugin_registered in RegisteredPlugin.objects.actives():
        enable_plugin(get_plugin_module_name(plugin_registered.directory_name))


def active_default_plugins(*args, **kwargs):
    if kwargs['sender'] == plugin_models:
        interactive = kwargs.get('interactive', None)
        if interactive:
            for plugin_dir in settings.ACTIVED_DEFAULTS_PLUGINS:
                plugin = register_plugin(plugin_dir)
                plugin.installed = True
                plugin.active = True
                plugin.save()


post_syncdb.connect(active_default_plugins)
