import os
import sys
import subprocess

from django.conf import settings
from django.core.cache import cache

from merengue.pluggable import PLUG_CACHE_KEY, register_plugin
from merengue.pluggable.utils import get_plugins_dir, is_plugin_broken, get_plugin_module_name


def check_plugins():
    """ check plugins found in file system and compare with registered
        one in database """
    # all process will be in a unique transaction, we don't want to get
    # self committed
    cache.delete(PLUG_CACHE_KEY)
    # now look for all plugins in filesystem and enable them
    for plugin_dir in os.listdir(os.path.join(settings.BASEDIR, get_plugins_dir())):
        register_plugin(plugin_dir)

    if settings.DETECT_BROKEN_PLUGINS:
        # we have to launch other process because broken plugin detection
        # tries to validate models and this register non valid meta information
        # (fields, m2m, etc.)
        process = subprocess.Popen(
            [sys.executable, 'manage.py', "mark_broken_plugins"],
            cwd=settings.BASEDIR,
        )
        process.wait()


def mark_broken_plugins():
    """
    Mark broken plugins (i.e. not existing in FS). This will prevent errors
    with python modules deleted from file system or broken modules.
    """
    from merengue.pluggable.models import RegisteredPlugin
    cleaned_items = []
    for registered_item in RegisteredPlugin.objects.inactives():
        plugin_name = get_plugin_module_name(registered_item.directory_name)
        if is_plugin_broken(plugin_name):
            registered_item.broken = True
            registered_item.save()
        else:
            cleaned_items.append(registered_item)
            if registered_item.broken:
                # in past was broken but now is ok
                registered_item.broken = False
                registered_item.save()
