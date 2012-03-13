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
from django.contrib.admin.sites import NotRegistered, AlreadyRegistered
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.exceptions import ImproperlyConfigured, FieldError, MiddlewareNotUsed
from django.core.management import call_command
from django.core.management.color import no_style
from django.core.management.sql import sql_all
from django.core.management.validation import get_validation_errors
from django.core import urlresolvers
from django.db import connection, transaction
from django.db.models import get_models
from django.db.models.loading import load_app, cache
from django.utils.importlib import import_module
from django.utils.translation import get_language, activate

from south import migration
from south.exceptions import NoMigrations

from merengue import registry
from merengue.base.adminsite import site
from merengue.block.utils import clear_lookup_cache
from merengue.registry.items import (NotRegistered as NotRegisteredItem)
from merengue.section.models import BaseSection
from merengue.section.middleware import register_section_prefix, unregister_section_prefix
from merengue.perms.utils import register_permission, unregister_permission
from merengue.pluggable.exceptions import BrokenPlugin
from merengue.pluggable.models import RegisteredPlugin


# ----- internal attributes and methods -----

_plugin_middlewares_cache = {
    'loaded_middlewares': [],
    'request_middleware': [],
    'view_middleware': [],
    'response_middleware': [],
    'exception_middleware': [],
}


def _get_url_resolver():
    try:
        return urlresolvers.get_resolver(import_module(urlresolvers.get_urlconf(settings.ROOT_URLCONF)))
    except AttributeError:
        # A weird error we can't reproduce but which is solved with this patch. See #2229
        return urlresolvers.get_resolver(import_module(settings.ROOT_URLCONF))


# ----- public methods -----


def install_plugin(registered_plugin):
    app_name = registered_plugin.directory_name
    plugin_name = get_plugin_module_name(app_name)
    # Needed update installed apps in order
    # to get SQL command from merengue.pluggable
    add_to_installed_apps(plugin_name)
    clear_plugin_module_cache(plugin_name)
    if load_app(plugin_name) and not are_installed_models(app_name):
        install_models(app_name)
        reload_models_cache()
        # Force registered_plugin saving after connection closes.
        registered_plugin.save()
    if registered_plugin.active:
        enable_plugin(plugin_name)
        # Doing extra custom installation implemented in each plugin
        plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
        plugin.post_install()
    else:
        disable_plugin(plugin_name)


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


def get_plugin(plugin_dir, prepend_plugins_dir=True):
    plugin_config = get_plugin_config(plugin_dir, prepend_plugins_dir)
    reg_plugin = RegisteredPlugin.objects.get_by_item_class(plugin_config)
    return reg_plugin.get_registry_item()


def validate_plugin(plugin_config):
    if not plugin_config.name:
        raise ImproperlyConfigured('Plugin %s must have a defined "name" attribute' % plugin_config)


def have_south(app_name):
    try:
        migrations = migration.Migrations(app_name)  # pyflakes:ignore
    except NoMigrations:
        return False
    else:
        return True


def are_installed_models(app_name):
    if have_south(app_name):
        return False
    app_module = load_app(get_plugin_module_name(app_name))
    plugin_models = get_models(app_module)
    tables = connection.introspection.table_names()
    seen_models = connection.introspection.installed_models(tables)
    for plugin_model in plugin_models:
        if not plugin_model in seen_models:
            return False
    return True


def install_models(app_name):
    app_module = load_app(get_plugin_module_name(app_name))
    if have_south(app_name):
        lang = get_language()
        # invalidate south cache to avoid very weird bugs (see #2025)
        migration.Migrations.invalidate_all_modules()
        migration.Migrations.calculate_dependencies(force=True)
        # migrate plugin with south
        call_command('migrate', app=app_name)
        # call_command activates a default 'en-us' locale in thread. we restore it
        activate(lang)
    else:
        style = no_style()
        cursor = connection.cursor()
        sql_commands = sql_all(app_module, style, connection)
        for sql_command in sql_commands:
            cursor.execute(sql_command)
    # update all content types
    update_all_contenttypes()
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
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for url_prefix, urlconf in plugin.get_url_prefixes():
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
        get_plugin_config(plugin_name)
        try:
            # try to import plugin modules (if exists) to validate those models
            models_modname = '%s.models' % get_plugin_module_name(plugin_name)
            models_module = import_module(models_modname)
            s = StringIO()
            num_errors = get_validation_errors(s, models_module)
            if num_errors:
                # the plugin was broken because some models validation break
                return True
        except ImportError:
            # usually means models module does not exists. Don't worry about that
            pass
        except (TypeError, FieldError, SyntaxError):  # some validation error when importing models
            raise BrokenPlugin(plugin_name, *sys.exc_info())
    except Exception:
        raise BrokenPlugin(plugin_name, *sys.exc_info())


def enable_plugin(plugin_name, register=True):
    from merengue.base.admin import register_app
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    add_to_installed_apps(plugin_name)
    if register:
        register_app(plugin_name)
        register_plugin_actions(plugin_name)
        register_plugin_blocks(plugin_name)
        register_plugin_toolbar(plugin_name)
        register_plugin_middlewares(plugin_name)
        register_plugin_viewlets(plugin_name)
        register_plugin_templatetags(plugin_name)
        register_plugin_post_actions(plugin_name)
        register_plugin_models(plugin_name)
        register_plugin_section_models(plugin_name)
        register_plugin_in_plugin_admin_site(plugin_name)
        register_plugin_perms(plugin_name)
        register_plugin_section_prefixes(plugin_name)
    register_plugin_urls(plugin_name)
    # activate plugin in DB
    registered_plugin = plugin.get_registered_item()
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
        unregister_plugin_toolbar(plugin_name)
        unregister_plugin_middlewares(plugin_name)
        unregister_plugin_viewlets(plugin_name)
        unregister_plugin_templatetags(plugin_name)
        unregister_plugin_models(plugin_name)
        unregister_plugin_section_models(plugin_name)
        unregister_plugin_in_plugin_admin_site(plugin_name)
        unregister_plugin_perms(plugin_name)
        unregister_plugin_section_prefixes(plugin_name)
    unregister_plugin_urls(plugin_name)
    # app_directories template loader loads app_template_dirs in
    # compile time, so we have to load it again.
    reload_app_directories_template_loader()
    # clear models cache to populate new models
    reload_models_cache()


def register_plugin_urls(plugin_name):
    for index, plugin_url in find_plugin_urls(plugin_name):
        if plugin_url and index < 0:
            urlpatterns = _get_url_resolver().url_patterns
            urlpatterns += (plugin_url, )
    update_admin_urls()
    urlresolvers.clear_url_caches()


def unregister_urlpattern(urlpattern, urlpatterns_list):
    urlpatterns_to_recurse = []
    for i, child_pattern in enumerate(urlpatterns_list):
        if hasattr(child_pattern, 'urlconf_module') and child_pattern.urlconf_module == urlpattern.urlconf_module:
            del urlpatterns_list[i]  # unregister URL pattern
            return
        if isinstance(child_pattern, urlresolvers.RegexURLResolver):
            urlpatterns_to_recurse.append(child_pattern.url_patterns)
    for child_url in urlpatterns_to_recurse:
        unregister_urlpattern(urlpattern, child_url)


def unregister_plugin_urls(plugin_name, urlpatterns=None):
    if urlpatterns is None:
        urlpatterns = _get_url_resolver().url_patterns
    for index, plugin_url in find_plugin_urls(plugin_name):
        if index > 0:
            unregister_urlpattern(plugin_url, urlpatterns)
    update_admin_urls()


def update_admin_urls(urlresolver=None):
    from merengue.base import admin
    if urlresolver is None:
        urlresolver = _get_url_resolver()
    for i, child_pattern in enumerate(urlresolver.url_patterns):
        if isinstance(child_pattern, urlresolvers.RegexURLResolver):
            if child_pattern.app_name == 'admin':
                urlresolver.url_patterns[i] = url(r'^admin/', include(admin.site.urls))
                return
            else:
                # does the recursion to find "admin" app in the child
                # with debug toolbar the admin is not in root urlconf
                update_admin_urls(child_pattern)
                child_pattern._populate()  # invalidate to allow reverse resolution


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
    for item_class in item_list:
        if not registry.have_registered_items(item_class):
            registry.register(item_class)


def unregister_items(item_list):
    try:
        for item_class in item_list:
            registry.unregister_all(item_class)
    except NotRegisteredItem:
        pass


def register_plugin_actions(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    register_items(plugin.get_actions())


def unregister_plugin_actions(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    unregister_items(plugin.get_actions())


def register_plugin_blocks(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    plugin_blocks = plugin.get_blocks()
    if plugin_blocks:
        register_items(plugin_blocks)
        clear_lookup_cache()


def unregister_plugin_blocks(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    plugin_blocks = plugin.get_blocks()
    if plugin_blocks:
        unregister_items(plugin_blocks)
        clear_lookup_cache()


def register_plugin_viewlets(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    register_items(plugin.get_viewlets())


def unregister_plugin_viewlets(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    unregister_items(plugin.get_viewlets())


def register_plugin_toolbar(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    register_items(plugin.get_toolbar_panels())


def unregister_plugin_toolbar(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    unregister_items(plugin.get_toolbar_panels())


def register_plugin_post_actions(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    plugin.post_actions()


def register_plugin_models(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for model, model_admin in plugin.models():
        try:
            site.register_model(model, model_admin)
        except AlreadyRegistered:
            pass


def register_plugin_section_models(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    register_plugin_section_models_in_admin_site(plugin, plugin_name, site)


def unregister_plugin_models(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for model, model_admin in plugin.models():
        site.unregister_model(model)


def unregister_plugin_section_models(plugin_name):
    pass


def register_plugin_section_models_in_admin_site(plugin, plugin_name, admin_site):
    if not admin_site:
        return
    for model, admin_model in plugin.section_models():
        try:
            site_related = admin_site.register_related(model, admin_model, related_to=BaseSection)
            plugin.section_register_hook(site_related, model)
        except AlreadyRegistered:
            pass


def register_plugin_in_plugin_admin_site(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    model_admins = plugin.get_model_admins()
    if not model_admins:
        return
    plugin_site = site.register_plugin_site(plugin_name)
    for model, admin_model in plugin.get_model_admins():
        try:
            plugin_site.register(model, admin_model)
        except AlreadyRegistered:
            pass


def unregister_plugin_in_plugin_admin_site(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    else:
        plugin = plugin.get_registered_item()
        if not plugin.installed:
            return
    site.unregister_plugin_site(plugin_name)


def register_plugin_perms(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for perm in plugin.get_perms():
        register_permission(*perm)


def unregister_plugin_perms(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for perm in plugin.get_perms():
        unregister_permission(perm[1])


def register_plugin_middlewares(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for middleware in plugin.get_middlewares():
        register_middleware(middleware)


def unregister_plugin_middlewares(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for middleware in plugin.get_middlewares():
        unregister_middleware(middleware)


def register_plugin_section_prefixes(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for section_prefix in plugin.get_section_prefixes():
        register_section_prefix(section_prefix)


def unregister_plugin_section_prefixes(plugin_name):
    plugin = get_plugin(plugin_name, prepend_plugins_dir=False)
    if not plugin:
        return
    for section_prefix in plugin.get_section_prefixes():
        unregister_section_prefix(section_prefix)


def reload_models_cache():
    """
    Reload Django internal cache for all models in installed apps.
    This includes model field mapping, related fields in _meta object, etc.
    """
    installed_app_names = [app.split('.')[-1] for app in settings.INSTALLED_APPS]
    for app_label in cache.app_models:
        if app_label not in installed_app_names:
            del cache.app_models[app_label]
    cache.loaded = False
    cache.handled = {}
    cache.app_store.clear()
    cache._populate()
    cache._get_models_cache.clear()
    for model in get_models():
        opts = model._meta
        if hasattr(opts, '_related_many_to_many_cache'):
            # we remove related m2m and fk fields cache for all models
            del opts._related_many_to_many_cache
            del opts._related_objects_cache
        opts.init_name_map()


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
        attr = func.__class__.__name__
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
        return  # already registered
    try:
        dot = middleware_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured('%s isn\'t a middleware module' % middleware_path)
    mw_module, mw_classname = middleware_path[:dot], middleware_path[dot + 1:]
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
        return  # not registered
    for midd_type in ('request_middleware', 'request_middleware',
                      'response_middleware', 'exception_middleware', ):
        for path, method in _plugin_middlewares_cache[midd_type]:
            if middleware_path == path:
                _plugin_middlewares_cache[midd_type].remove((path, method))
    _plugin_middlewares_cache['loaded_middlewares'].remove(middleware_path)


def get_plugins_middleware_methods(midd_type):
    global _plugin_middlewares_cache
    return (t[1] for t in _plugin_middlewares_cache[midd_type])


def register_dummy_plugin(plugin_name):
    """ Register a dummy plugin. Useful when we cannot access to the PluginConfig """
    try:
        registered_plugin = RegisteredPlugin.objects.get(
            directory_name=plugin_name,
        )
    except RegisteredPlugin.DoesNotExist:
        registered_plugin = RegisteredPlugin.objects.create(
            directory_name=plugin_name, broken=True,  # it's important to create with broken=True
        )
    registered_plugin.broken = True
    registered_plugin.class_name = 'PluginConfig'
    registered_plugin.module = '%s.%s.config' % (settings.PLUGINS_DIR, plugin_name)
    registered_plugin.name = plugin_name
    registered_plugin.save()
    return registered_plugin


def clear_plugin_module_cache(plugin_module):
    for module_name, module in sys.modules.items():
        if module_name.startswith(plugin_module) and 'migrations' not in module_name:
            del sys.modules[module_name]


from merengue.section.admin import register as register_section
register_section(site)
