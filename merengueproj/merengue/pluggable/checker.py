import os
import sys
import subprocess

from django.conf import settings

from merengue.pluggable.loading import load_plugins
from merengue.pluggable.utils import is_plugin_broken, get_plugin_module_name


def check_plugins():
    """ check plugins found in file system and compare with registered
        one in database """
    # all process will be in a unique transaction, we don't want to get
    # self committed
    process_environ = {
        'PYTHONPATH': ':'.join(sys.path),
        'DJANGO_SETTINGS_MODULE': os.environ['DJANGO_SETTINGS_MODULE'],
    }

    if settings.DETECT_NEW_PLUGINS:
        # now look for all plugins in filesystem and register them
        # we have to launch other process because broken plugin detection
        # tries to validate models and this register non valid meta information
        # (fields, m2m, etc.)
        process = subprocess.Popen(
            [sys.executable, 'manage.py', "register_new_plugins"],
            cwd=settings.BASEDIR, env=process_environ,
        )
        process.wait()

    if settings.DETECT_BROKEN_PLUGINS:
        # we have to launch other process because broken plugin detection
        # tries to validate models and this register non valid meta information
        # (fields, m2m, etc.)
        process = subprocess.Popen(
            [sys.executable, 'manage.py', "mark_broken_plugins"],
            cwd=settings.BASEDIR, env=process_environ,
        )
        process.wait()

    # finally, we reload active plugins
    load_plugins()


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
