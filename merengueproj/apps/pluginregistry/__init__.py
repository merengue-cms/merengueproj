from django.conf import settings
from django.utils.importlib import import_module
from django.utils._os import safe_join


def get_plugins_dir():
    """ Returns plugins directory """
    plugins_dir = getattr(settings, 'PLUGINS_DIR', 'plugins')
    return plugins_dir


def get_plugin_config(plugin_dir):
    try:
        return import_module(safe_join(get_plugins_dir(), plugin_dir, 'config'))
    except ImportError:
        return None
