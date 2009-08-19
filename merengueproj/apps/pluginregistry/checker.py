import os

from django.db import transaction

from pluginregistry.utils import get_plugin_config, get_plugins_dir
from pluginregistry.models import Plugin


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
                params = {'directory_name': plugin_dir}
                plugin, created = Plugin.objects.get_or_create(**params)
                plugin.name = getattr(plugin_config, 'NAME', plugin_dir)
                plugin.description = getattr(plugin_config, 'DESCRIPTION', '')
                plugin.version = getattr(plugin_config, 'VERSION', '')
                plugin.save()
    except:
        transaction.savepoint_rollback(sid)
        raise
    else:
        transaction.savepoint_commit(sid)
