import os

from django.conf import settings
from django.db import transaction
from django.core.cache import cache

from merengue.plugins import PLUG_CACHE_KEY
from merengue.plugins.utils import get_plugin_config, get_plugins_dir
from merengue.plugins.models import RegisteredPlugin
from merengue.registry import register, is_registered


def check_plugins():
    """ check plugins found in file system and compare with registered
        one in database """
    # all process will be in a unique transaction, we don't want to get
    # self committed
    cache.delete(PLUG_CACHE_KEY)
    sid = transaction.savepoint()
    try:
        # now look for all plugins in filesystem and enable them
        for plugin_dir in os.listdir(os.path.join(settings.BASEDIR, get_plugins_dir())):
            register_plugin(plugin_dir)
    except:
        transaction.savepoint_rollback(sid)
        raise
    else:
        transaction.savepoint_commit(sid)


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
