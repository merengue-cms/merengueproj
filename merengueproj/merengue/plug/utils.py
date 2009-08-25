import os
import sys

from django.conf import settings
from django.conf.urls.defaults import include, url
from django.contrib.admin.sites import AlreadyRegistered, NotRegistered
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import no_style
from django.core.management.sql import sql_all
from django.db import connection, transaction
from django.db.models import get_models
from django.utils.importlib import import_module

from merengue import registry
from merengue.base.admin import register_app, unregister_app
from merengue.registry.items import (NotRegistered as NotRegisteredItem,
                            AlreadyRegistered as AlreadyRegisteredItem)


def get_plugins_dir():
    """Return plugins directory (settings.PLUGINS_DIR)."""
    plugins_dir = getattr(settings, 'PLUGINS_DIR', 'plugins')
    return plugins_dir


def get_plugin_module_name(plugin_dir):
    return '%s.%s' % (get_plugins_dir(), plugin_dir)


def get_plugin_config(plugin_dir, prepend_plugins_dir=True):
    try:
        if prepend_plugins_dir:
            plugin_modname = '%s.config' % get_plugin_module_name(plugin_dir)
        else:
            plugin_modname = '%s.config' % plugin_dir
        return getattr(import_module(plugin_modname), 'PluginConfig')
    except (ImportError, TypeError, ValueError):
        return None


def are_installed_models(plugin_mod):
    installed = True
    plugin_models = get_models(plugin_mod)
    try:
        [m.objects.all().count() for m in plugin_models]
    except:
        connection.close()
        installed = False
    return installed


def install_models(plugin_mod):
    style = no_style()
    cursor = connection.cursor()
    sql_commands = sql_all(plugin_mod, style)
    for sql_command in sql_commands:
        cursor.execute(sql_command)
    transaction.commit_unless_managed()


def add_to_installed_apps(plugin_name):
    if not plugin_name in settings.INSTALLED_APPS:
        if isinstance(settings.INSTALLED_APPS, list):
            settings.INSTALLED_APPS.append(plugin_name)
        else:
            settings.INSTALLED_APPS = tuple(
                list(settings.INSTALLED_APPS) + [plugin_name],
            )


def remove_from_installed_apps(plugin_name):
    if plugin_name in settings.INSTALLED_APPS:
        if isinstance(settings.INSTALLED_APPS, list):
            settings.INSTALLED_APPS.remove(plugin_name)
        else:
            settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
            settings.INSTALLED_APPS.remove(plugin_name)
            settings.INSTALLED_APPS = tuple(settings.INSTALLED_APPS)


def find_plugin_url(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    plugin_url_re = r'^%s/' % plugin_config.url_prefix
    plugin_url_name = "%s.urls" % plugin_name
    try:
        import_module(plugin_url_name)
    except ImportError:
        return (-1, None)
    plugin_url = url(plugin_url_re, include(plugin_url_name), name=plugin_name)
    proj_urls = import_module(settings.ROOT_URLCONF)
    urlconf_names = [
        getattr(p, 'urlconf_name', None) for p in proj_urls.urlpatterns]
    index = -1
    if plugin_url_name in urlconf_names:
        index = urlconf_names.index(plugin_url_name)
    return (index, plugin_url)


def enable_plugin(plugin_name, register=True):
    from merengue.plug import PLUG_CACHE_KEY
    cache.delete(PLUG_CACHE_KEY)
    add_to_installed_apps(plugin_name)
    if register:
        try:
            register_app(plugin_name)
        except AlreadyRegistered:
            pass
        register_plugin_actions(plugin_name)
        register_plugin_blocks(plugin_name)
    register_plugin_urls(plugin_name)


def disable_plugin(plugin_name, unregister=True):
    from merengue.plug import PLUG_CACHE_KEY
    cache.delete(PLUG_CACHE_KEY)
    remove_from_installed_apps(plugin_name)
    if unregister:
        try:
            unregister_app(plugin_name)
        except NotRegistered:
            pass
        unregister_plugin_actions(plugin_name)
        unregister_plugin_blocks(plugin_name)
    unregister_plugin_urls(plugin_name)


def register_plugin_urls(plugin_name):
    index, plugin_url = find_plugin_url(plugin_name)
    if plugin_url and index < 0:
        proj_urls = import_module(settings.ROOT_URLCONF)
        proj_urls.urlpatterns += (plugin_url, )


def unregister_plugin_urls(plugin_name):
    index, plugin_url = find_plugin_url(plugin_name)
    if index > 0:
        proj_urls = import_module(settings.ROOT_URLCONF)
        del proj_urls.urlpatterns[index]


def register_items(item_list):
    try:
        for item_class in item_list:
            registry.register(item_class)
    except AlreadyRegisteredItem:
        pass


def unregister_items(item_list):
    try:
        for item_class in item_list:
            registry.unregister(item_class)
    except NotRegisteredItem:
        pass


def register_plugin_actions(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    register_items(plugin_config.get_actions())


def unregister_plugin_actions(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    unregister_items(plugin_config.get_actions())


def register_plugin_blocks(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    register_items(plugin_config.get_blocks())


def unregister_plugin_blocks(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    unregister_items(plugin_config.get_blocks())


def reload_app_directories_template_loader():
    from django.template import loader
    template_loader_app_directories = 'django.template.loaders.' \
                                      'app_directories.load_template_source'
    if not loader.template_source_loaders:
        return
    for func in loader.template_source_loaders:
        module = func.__module__
        attr = func.__name__
        template_loader_name = "%s.%s" % (module, attr)
        if template_loader_app_directories == template_loader_name:
            try:
                mod = import_module(module)
            except ImportError, e:
                msg = 'Error importing template source loader %s: "%s"' \
                      % (module, e)
                raise (ImproperlyConfigured, msg)
            sys_fs_encoding = sys.getfilesystemencoding()
            sys_default_encoding = sys.getdefaultencoding()
            fs_encoding = sys_fs_encoding or sys_default_encoding
            app_template_dirs = []
            for app in settings.INSTALLED_APPS:
                try:
                    mod = import_module(app)
                except ImportError, e:
                    msg = 'ImportError %s: %s' % (app, e.args[0])
                    raise (ImproperlyConfigured, msg)
                template_dir = os.path.join(os.path.dirname(mod.__file__),
                                            'templates')
                if os.path.isdir(template_dir):
                    app_template_dirs.append(template_dir.decode(fs_encoding))
            app_template_dirs = tuple(app_template_dirs)
            from django.template.loaders import app_directories
            app_directories.app_template_dirs = app_template_dirs
