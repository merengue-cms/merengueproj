import os

from django.conf import settings
from django.core.cache import cache

from merengue.plugin import PLUG_CACHE_KEY, register_plugin
from merengue.plugin.utils import get_plugins_dir


def check_plugins():
    """ check plugins found in file system and compare with registered
        one in database """
    # all process will be in a unique transaction, we don't want to get
    # self committed
    cache.delete(PLUG_CACHE_KEY)
    # now look for all plugins in filesystem and enable them
    for plugin_dir in os.listdir(os.path.join(settings.BASEDIR, get_plugins_dir())):
        register_plugin(plugin_dir)
