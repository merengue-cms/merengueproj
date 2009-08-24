import os

from django.db import transaction

from plug.utils import get_plugin_config, get_plugins_dir
from plug.models import RegisteredPlugin
from registry import register, is_registered


def check_plugins():
    """ check plugins found in file system and compare with registered
        one in database """
    # all process will be in a unique transaction, we don't want to get
    # self committed
    sid = transaction.savepoint()
    try:
        # now look for all plugins in filesystem and enable them
        for plugin_dir in os.listdir(get_plugins_dir()):
            plugin_config = get_plugin_config(plugin_dir)
            if plugin_config:
                if not is_registered(plugin_config):
                    register(plugin_config)
                plugin = RegisteredPlugin.objects.get_by_item(plugin_config)
                plugin.name = getattr(plugin_config, 'name', plugin_dir)
                plugin.directory_name = plugin_dir
                plugin.description = getattr(plugin_config, 'description', '')
                plugin.version = getattr(plugin_config, 'version', '')
                plugin.save()
    except:
        transaction.savepoint_rollback(sid)
        raise
    else:
        transaction.savepoint_commit(sid)
