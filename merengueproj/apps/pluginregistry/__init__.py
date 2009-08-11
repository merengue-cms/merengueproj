import os
import sys

from django.conf import settings
from django.contrib.admin.sites import AlreadyRegistered, NotRegistered
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import no_style
from django.core.management.sql import sql_all
from django.db import connection, transaction
from django.db.models import get_models
from django.utils.importlib import import_module

from merengue.admin import register_app, unregister_app


def get_plugins_dir():
    """ Returns plugins directory """
    plugins_dir = getattr(settings, 'PLUGINS_DIR', 'plugins')
    return plugins_dir


def get_plugin_module_name(plugin_dir):
    return '%s.%s' % (get_plugins_dir(), plugin_dir)


def get_plugin_config(plugin_dir):
    try:
        plugin_modname = '%s.config' % get_plugin_module_name(plugin_dir)
        return import_module(plugin_modname)
    except (ImportError, TypeError, ValueError):
        if plugin_dir == 'news':
            raise
        return None


def are_installed_models(app_mod):
    installed = True
    app_models = get_models(app_mod)
    try:
        [m.objects.all().count() for m in app_models]
    except:
        connection.close()
        installed = False
    return installed


def install_models(app_mod):
    style = no_style()
    cursor = connection.cursor()
    sql_commands = sql_all(app_mod, style)
    for sql_command in sql_commands:
        cursor.execute(sql_command)
    transaction.commit_unless_managed()


def add_to_installed_apps(app_name):
    if not app_name in settings.INSTALLED_APPS:
        if isinstance(settings.INSTALLED_APPS, list):
            settings.INSTALLED_APPS.append(app_name)
        else:
            settings.INSTALLED_APPS = tuple(
                list(settings.INSTALLED_APPS) + [app_name],
            )


def remove_from_installed_apps(app_name):
    if app_name in settings.INSTALLED_APPS:
        if isinstance(settings.INSTALLED_APPS, list):
            settings.INSTALLED_APPS.remove(app_name)
        else:
            settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
            settings.INSTALLED_APPS.remove(app_name)
            settings.INSTALLED_APPS = tuple(settings.INSTALLED_APPS)


def enable_plugin(app_name):
    add_to_installed_apps(app_name)
    try:
        register_app(app_name)
    except AlreadyRegistered:
        pass


def disable_plugin(app_name):
    remove_from_installed_apps(app_name)
    try:
        unregister_app(app_name)
    except NotRegistered:
        pass


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
