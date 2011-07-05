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

from django.conf import settings
from django.utils.translation import ugettext

from south.signals import post_migrate
from transmeta import get_fallback_fieldname

from merengue.registry import register, have_registered_items
from merengue.registry.items import RegistrableItem
from merengue.registry.models import RegisteredItem
from merengue.utils import is_last_application, classproperty


class Plugin(RegistrableItem):
    singleton = True
    url_prefixes = ()
    active_by_default = False

    def get_url_prefixes(self):
        prefixes = []
        for url_prefix, url in self.url_prefixes:
            prefix = url_prefix
            if isinstance(url_prefix, dict):
                prefix = url_prefix.get(
                    getattr(settings, 'URL_DEFAULT_LANG', settings.LANGUAGE_CODE),
                )
            prefixes.append((prefix, url))

        return prefixes

    @classmethod
    def get_category(cls):
        return 'plugin'

    @classproperty
    @classmethod
    def model(self):
        from merengue.pluggable.models import RegisteredPlugin
        return RegisteredPlugin

    def _get_registered_items(self, item_classes):
        for item_class in item_classes:
            reg_item = RegisteredItem.objects.get_by_item_class(item_class)
            yield reg_item.get_registry_item()

    def get_actions(self):
        return []  # to override in plugins

    def get_actions_items(self):
        return []  # to override in plugins

    def get_blocks(self):
        return []  # to override in plugins

    def get_middlewares(self):
        return []  # to override in plugins

    def get_viewlets(self):
        return []  # to override in plugins

    def post_actions(self):
        pass

    def models(self):
        return []  # to override in plugins

    def section_models(self):
        return []  # to override in plugins

    def section_register_hook(self, site_related, model):
        pass

    def get_model_admins(self):
        return []  # to override in plugins

    def get_perms(self):
        return []  # to override in plugins

    def get_toolbar_panels(self):
        return []  # to override in plugins

    def get_section_prefixes(self):
        return []  # to override in plugins

    def post_install(self):
        pass

    def get_notifications(self):
        return []  # to override in plugins

    def get_blocks_items(self):
        return self._get_registered_items(self.get_blocks())

    def get_toolbar_panels_items(self):
        return self._get_registered_items(self.get_toolbar_panels())

    def get_viewlets_items(self):
        return self._get_registered_items(self.get_viewlets())


def register_plugin(plugin_dir):
    from merengue.pluggable.models import RegisteredPlugin
    from merengue.pluggable.utils import get_plugin_config, validate_plugin
    plugin_config = get_plugin_config(plugin_dir)
    if plugin_config:
        validate_plugin(plugin_config)
        try:
            reg_plugin = RegisteredPlugin.objects.get_by_item_class(plugin_config)
        except RegisteredPlugin.DoesNotExist:
            reg_plugin = register(plugin_config)
        plugin = reg_plugin.get_registry_item()
        reg_plugin.name = getattr(plugin, 'name')
        reg_plugin.directory_name = plugin_dir
        reg_plugin.description = getattr(plugin, 'description', '')
        reg_plugin.version = getattr(plugin, 'version', '')
        reg_plugin.required_apps = getattr(plugin, 'required_apps',
                                           None)
        reg_plugin.required_plugins = getattr(plugin,
                                              'required_plugins',
                                              None)
        reg_plugin.meta_info = {}
        if hasattr(plugin, 'screenshot'):
            reg_plugin.meta_info['screenshot'] = plugin.screenshot
        reg_plugin.meta_info['actions'] = []
        for action in plugin.get_actions():
            reg_plugin.meta_info['actions'].append({'name': unicode(action.name), 'help_text': unicode(action.help_text)})
        reg_plugin.meta_info['blocks'] = []
        for block in plugin.get_blocks():
            reg_plugin.meta_info['blocks'].append({'name': unicode(block.name), 'help_text': unicode(block.help_text)})
        if plugin.get_model_admins():
            reg_plugin.meta_info['has_own_admin'] = True
        else:
            reg_plugin.meta_info['has_own_admin'] = False
        reg_plugin.meta_info['middlewares'] = []
        for middleware in plugin.get_middlewares():
            reg_plugin.meta_info['middlewares'].append(middleware)
        reg_plugin.meta_info['section_models'] = []
        for model, admin in plugin.section_models():
            reg_plugin.meta_info['section_models'].append({'name': unicode(model._meta.verbose_name)})
        reg_plugin.meta_info['viewlets'] = []
        for viewlet in plugin.get_viewlets():
            reg_plugin.meta_info['viewlets'].append({'name': unicode(viewlet.name), 'help_text': unicode(viewlet.help_text)})

        if "notification" in settings.INSTALLED_APPS:
            from notification.models import create_notice_type
            for notification in plugin.get_notifications():
                label, display, description = notification
                create_notice_type(label, display, description)

        reg_plugin.save()
        return reg_plugin
    return None


def enable_active_plugins():
    from merengue.pluggable.models import RegisteredPlugin
    from merengue.pluggable.utils import enable_plugin, get_plugin_module_name, reload_models_cache
    for plugin_registered in RegisteredPlugin.objects.actives():
        enable_plugin(get_plugin_module_name(plugin_registered.directory_name))
    reload_models_cache()


def register_all_plugins(verbose=False):
    from merengue.pluggable.models import RegisteredPlugin
    from merengue.pluggable.utils import (get_plugin_directories, get_plugin_config,
                                          reload_models_cache, remove_from_installed_apps,
                                          clear_plugin_module_cache, get_plugin_module_name)
    from merengue.pluggable.checker import mark_broken_plugin
    try:
        for plugin_dir in get_plugin_directories():
            try:
                if verbose:
                    plugin_config = get_plugin_config(plugin_dir)
                    if plugin_config:
                        if not have_registered_items(plugin_config):
                            print 'Registering new plugin %s...' % plugin_dir
                        else:
                            print 'Re-registering plugin %s...' % plugin_dir
                    else:
                        print 'Error walking to plugin %s.' % plugin_dir
                register_plugin(plugin_dir)
            except:
                mark_broken_plugin(plugin_dir)
                print 'Error registering %s plugin... go to next plugin.' % plugin_dir
    finally:
        for plugin in RegisteredPlugin.objects.inactives():
            clear_plugin_module_cache(get_plugin_module_name(plugin.directory_name))
            remove_from_installed_apps(plugin.directory_name)
        reload_models_cache()


def active_default_plugins(*args, **kwargs):
    """ active default plugins and creates the portal menu in each language """
    # Only want to run this signal after all application was migrated, but
    # south have not a "post all migrations" signal.
    # The workaround is "collab" have to be the last application migrated
    if is_last_application(kwargs['app']):
        # register required plugins
        for plugin_dir in settings.REQUIRED_PLUGINS:
            active_plugin_with_deps(plugin_dir)
        # populate menu
        from merengue.section.models import Menu
        name_attr = get_fallback_fieldname('name')
        attrs = {name_attr: 'Portal menu', 'slug': settings.MENU_PORTAL_SLUG}
        try:
            portal_menu = Menu.objects.get(slug=settings.MENU_PORTAL_SLUG)
        except Menu.DoesNotExist:
            # creating portal menu if does not exist
            portal_menu = Menu.objects.create(**attrs)
            for lang_code, lang_text in settings.LANGUAGES:
                setattr(portal_menu, 'name_%s' % lang_code, ugettext('portal menu'))
            portal_menu.save()


def active_plugin_with_deps(plugin_dir):
    """ active plugins with its dependences """
    from merengue.pluggable.utils import install_plugin
    registered_plugin = register_plugin(plugin_dir)
    plugin = registered_plugin.get_registry_item()
    for dep in getattr(plugin, 'required_plugins', []):
        active_plugin_with_deps(dep)
    registered_plugin.installed = True
    registered_plugin.active = True
    registered_plugin.save()
    install_plugin(registered_plugin)


post_migrate.connect(active_default_plugins)
