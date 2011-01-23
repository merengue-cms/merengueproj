# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-

import os
import sys
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO  # pyflakes:ignore

from django import templatetags
from django.conf import settings
from django.conf.urls.defaults import include, url
from django.contrib.admin.sites import NotRegistered
from django.core.exceptions import ImproperlyConfigured, FieldError, MiddlewareNotUsed
from django.core.management.color import no_style
from django.core.management.sql import sql_all
from django.core.management.validation import get_validation_errors
from django.core import urlresolvers
from django.db import connection, transaction
from django.db.models import get_models
from django.db.models.loading import load_app
from django.utils.importlib import import_module

from merengue import registry
from merengue.base.adminsite import site
from merengue.registry.items import (NotRegistered as NotRegisteredItem,
                                     AlreadyRegistered as AlreadyRegisteredItem)
from merengue.section.models import Section
from merengue.perms.utils import register_permission, unregister_permission
from merengue.pluggable.exceptions import BrokenPlugin


# ----- internal attributes and methods -----


_plugin_middlewares_cache = {
    'loaded_middlewares': [],
    'request_middleware': [],
    'view_middleware': [],
    'response_middleware': [],
    'exception_middleware': [],
}


# ----- public methods -----


def install_plugin(registered_plugin):
    app_name = get_plugin_module_name(registered_plugin.directory_name)
    app_mod = load_app(app_name)
    # Needed update installed apps in order
    # to get SQL command from merengue.pluggable
    add_to_installed_apps(app_name)
    if app_mod and not are_installed_models(app_mod):
        install_models(app_mod)
        # Force registered_plugin saving after connection closes.
        registered_plugin.save()
    if registered_plugin.active:
        enable_plugin(app_name)
    else:
        disable_plugin(app_name)


def get_plugins_dir():
    """Return plugins directory (settings.PLUGINS_DIR)."""
    plugins_dir = getattr(settings, 'PLUGINS_DIR', 'plugins')
    return plugins_dir


def get_plugin_directories():
    """ get all plugins directories """
    plugins_path = os.path.join(settings.BASEDIR, get_plugins_dir())
    return [d for d in os.listdir(plugins_path) if os.path.isdir(os.path.join(plugins_path, d)) and
                                                   not d.startswith('.')]


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
        # only will raise exception in debug mode
        # this prevents broke the whole portal when registering a broken plugin
        if settings.DEBUG:
            raise
        return None


def validate_plugin(plugin_config):
    if not plugin_config.name:
        raise ImproperlyConfigured('Plugin %s must have a defined "name" attribute' % plugin_config)


def are_installed_models(plugin_mod):
    plugin_models = get_models(plugin_mod)
    tables = connection.introspection.table_names()
    seen_models = connection.introspection.installed_models(tables)
    for plugin_model in plugin_models:
        if not plugin_model in seen_models:
            return False
    return True


def install_models(plugin_mod):
    style = no_style()
    cursor = connection.cursor()
    sql_commands = sql_all(plugin_mod, style)
    for sql_command in sql_commands:
        cursor.execute(sql_command)
    transaction.commit()


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


def find_plugin_urls(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    for url_prefix, urlconf in plugin_config.url_prefixes:
        plugin_url_re = r'^%s/' % url_prefix
        try:
            import_module(urlconf)
        except ImportError:
            yield (-1, None)
        plugin_url = url(plugin_url_re, include(urlconf), name=plugin_name)
        proj_urls = urlresolvers.get_resolver(None)
        urlconf_names = [
            getattr(p, 'urlconf_name', None) for p in proj_urls.url_patterns]
        index = -1
        if urlconf in urlconf_names:
            index = urlconf_names.index(urlconf)
        yield (index, plugin_url)


def check_plugin_broken(plugin_name):
    """ Check if plugin is broken (i.e. not exist in file system) and raises an exception """
    try:
        get_plugin_config(plugin_name, prepend_plugins_dir=False)
        try:
            # try to import plugin modules (if exists) to validate those models
            models_modname = '%s.models' % plugin_name
            models_module = import_module(models_modname)
            s = StringIO()
            num_errors = get_validation_errors(s, models_module)
            if num_errors:
                # the plugin was broken because some models validation break
                return True
        except ImportError:
            # usually means models module does not exists. Don't worry about that
            pass
        except (TypeError, FieldError, SyntaxError): # some validation error when importing models
            raise BrokenPlugin(plugin_name, *sys.exc_info())
    except Exception:
        raise BrokenPlugin(plugin_name, *sys.exc_info())


def enable_plugin(plugin_name, register=True):
    from merengue.base.admin import register_app
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    add_to_installed_apps(plugin_name)
    if register:
        register_app(plugin_name)
        register_plugin_actions(plugin_name)
        register_plugin_blocks(plugin_name)
        register_plugin_middlewares(plugin_name)
        register_plugin_viewlets(plugin_name)
        register_plugin_templatetags(plugin_name)
        register_plugin_post_actions(plugin_name)
        register_plugin_section_models(plugin_name)
        register_plugin_in_plugin_admin_site(plugin_name)
        register_plugin_perms(plugin_name)
    register_plugin_urls(plugin_name)
    # activate plugin in DB
    registered_plugin = plugin_config.get_registered_item()
    registered_plugin.activate()
    # app_directories template loader loads app_template_dirs in
    # compile time, so we have to load it again.
    reload_app_directories_template_loader()


def disable_plugin(plugin_name, unregister=True):
    from merengue.base.admin import unregister_app
    remove_from_installed_apps(plugin_name)
    if unregister:
        try:
            unregister_app(plugin_name)
        except NotRegistered:
            pass
        unregister_plugin_actions(plugin_name)
        unregister_plugin_blocks(plugin_name)
        unregister_plugin_middlewares(plugin_name)
        unregister_plugin_viewlets(plugin_name)
        unregister_plugin_templatetags(plugin_name)
        unregister_plugin_section_models(plugin_name)
        unregister_plugin_in_plugin_admin_site(plugin_name)
        unregister_plugin_perms(plugin_name)
    unregister_plugin_urls(plugin_name)
    # app_directories template loader loads app_template_dirs in
    # compile time, so we have to load it again.
    reload_app_directories_template_loader()


def register_plugin_urls(plugin_name):
    for index, plugin_url in find_plugin_urls(plugin_name):
        if plugin_url and index < 0:
            proj_urls = import_module(settings.ROOT_URLCONF)
            proj_urls.urlpatterns += (plugin_url, )
    update_admin_urls()


def unregister_plugin_urls(plugin_name):
    for index, plugin_url in find_plugin_urls(plugin_name):
        if index > 0:
            proj_urls = import_module(settings.ROOT_URLCONF)
            del proj_urls.urlpatterns[index]
    update_admin_urls()


def update_admin_urls():
    from merengue.base import admin
    urlconf = import_module(settings.ROOT_URLCONF)
    url_patterns = urlconf.urlpatterns
    for i, url_pattern in enumerate(url_patterns):
        if getattr(url_pattern, 'app_name', '') == 'admin':
            urlresolvers.clear_url_caches()
            urlconf.urlpatterns[i] = url(r'^admin/', include(admin.site.urls))


def register_plugin_templatetags(plugin_name):
    try:
        templatetags_mod = import_module('%s.templatetags' % plugin_name)
        if templatetags_mod.__path__ not in templatetags.__path__:
            templatetags.__path__.extend(templatetags_mod.__path__)
    except ImportError:
        pass


def unregister_plugin_templatetags(plugin_name):
    try:
        templatetags_mod = import_module('%s.templatetags' % plugin_name)
        if templatetags_mod.__path__ in templatetags.__path__:
            templatetags.__path__.remove(templatetags_mod.__path__)
    except ImportError:
        pass


def register_items(item_list):
    try:
        for item_class in item_list:
            registry.register(item_class, activate=True)
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
    if not plugin_config:
        return
    register_items(plugin_config.get_actions())


def unregister_plugin_actions(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    unregister_items(plugin_config.get_actions())


def register_plugin_blocks(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    register_items(plugin_config.get_blocks())


def unregister_plugin_blocks(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    unregister_items(plugin_config.get_blocks())


def register_plugin_viewlets(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    register_items(plugin_config.get_viewlets())


def unregister_plugin_viewlets(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    unregister_items(plugin_config.get_viewlets())


def register_plugin_post_actions(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    plugin_config.post_actions()
    plugin_config.hook_post_register()


def register_plugin_section_models(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    register_plugin_section_models_in_admin_site(plugin_config, plugin_name, site)


def register_plugin_section_models_in_admin_site(plugin_config, plugin_name, admin_site):
    if not admin_site:
        return
    for model, admin_model in plugin_config.section_models():
        site_related = admin_site.register_related(model, admin_model, related_to=Section)
        plugin_config.section_register_hook(site_related, model)


def register_plugin_in_plugin_admin_site(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    model_admins = plugin_config.get_model_admins()
    if not model_admins:
        return
    plugin_site = site.register_plugin_site(plugin_name)
    for model, admin_model in plugin_config.get_model_admins():
        plugin_site.register(model, admin_model)


def register_plugin_perms(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    for perm in plugin_config.get_perms():
        register_permission(*perm)


def unregister_plugin_perms(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    for perm in plugin_config.get_perms():
        unregister_permission(perm[1])


def register_plugin_middlewares(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    for middleware in plugin_config.get_middlewares():
        register_middleware(middleware)


def unregister_plugin_middlewares(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    for middleware in plugin_config.get_middlewares():
        unregister_middleware(middleware)


def unregister_plugin_section_models(plugin_name):
    pass


def unregister_plugin_in_plugin_admin_site(plugin_name):
    plugin_config = get_plugin_config(plugin_name, prepend_plugins_dir=False)
    if not plugin_config:
        return
    else:
        plugin = plugin_config.get_registered_item()
        if not plugin.installed:
            return
    site.unregister_plugin_site(plugin_name)


def reload_app_directories_template_loader():
    """
    This function reloads the template directories with new apps installed.
    """
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


def has_required_dependencies(plugin):
    required_apps = plugin.required_apps or []
    for app in required_apps:
        if app not in settings.INSTALLED_APPS:
            return False
    required_plugins = plugin.required_plugins or {}
    from merengue.pluggable.models import RegisteredPlugin
    for plugin, properties in required_plugins.iteritems():
        filter_plugins = {'directory_name': plugin, 'active': True}
        # HACK: Key for filter params dict can't be unicode strings
        for attr, value in properties.iteritems():
            filter_plugins.update({str(attr): value})
        if not RegisteredPlugin.objects.filter(**filter_plugins):
            return False
    return True


def register_middleware(middleware_path):
    """
    Load middleware into plugin middleware registry
    """
    global _plugin_middlewares_cache
    if middleware_path in _plugin_middlewares_cache['loaded_middlewares']:
        return # already registered
    try:
        dot = middleware_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured('%s isn\'t a middleware module' % middleware_path)
    mw_module, mw_classname = middleware_path[:dot], middleware_path[dot+1:]
    try:
        mod = import_module(mw_module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing middleware %s: "%s"' % (mw_module, e))
    try:
        mw_class = getattr(mod, mw_classname)
    except AttributeError:
        raise ImproperlyConfigured('Middleware module "%s" does not define a "%s" class' % (mw_module, mw_classname))

    try:
        mw_instance = mw_class()
    except MiddlewareNotUsed:
        return

    if hasattr(mw_instance, 'process_request'):
        _plugin_middlewares_cache['request_middleware'].append(
            (middleware_path, mw_instance.process_request),
        )
    if hasattr(mw_instance, 'process_view'):
        _plugin_middlewares_cache['view_middleware'].append(
            (middleware_path, mw_instance.process_view),
        )
    if hasattr(mw_instance, 'process_response'):
        _plugin_middlewares_cache['response_middleware'].insert(
            0, (middleware_path, mw_instance.process_response),
        )
    if hasattr(mw_instance, 'process_exception'):
        _plugin_middlewares_cache['exception_middleware'].insert(
            0, (middleware_path, mw_instance.process_exception),
        )
    _plugin_middlewares_cache['loaded_middlewares'].append(middleware_path)


def unregister_middleware(middleware_path):
    """
    Unload middleware into plugin middleware registry
    """
    global _plugin_middlewares_cache
    if middleware_path not in _plugin_middlewares_cache['loaded_middlewares']:
        return # not registered
    for midd_type in ('request_middleware', 'request_middleware',
                      'response_middleware', 'exception_middleware', ):
        for path, method in _plugin_middlewares_cache[midd_type]:
            if middleware_path == path:
                _plugin_middlewares_cache[midd_type].remove((path, method))
    _plugin_middlewares_cache['loaded_middlewares'].remove(middleware_path)


def get_plugins_middleware_methods(midd_type):
    global _plugin_middlewares_cache
    return (t[1] for t in _plugin_middlewares_cache[midd_type])


from merengue.section.admin import register as register_section
register_section(site)
