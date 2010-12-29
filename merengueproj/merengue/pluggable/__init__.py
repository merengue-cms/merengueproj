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

from merengue.registry import register, is_registered
from merengue.registry.items import RegistrableItem
from merengue.utils import is_last_application, classproperty


class Plugin(RegistrableItem):
    url_prefixes = ()

    @classproperty
    @classmethod
    def model(cls):
        from merengue.pluggable.models import RegisteredPlugin
        return RegisteredPlugin

    @classmethod
    def get_category(cls):
        return 'plugin'

    @classmethod
    def get_actions(cls):
        return [] # to override in plugins

    @classmethod
    def get_blocks(cls):
        return [] # to override in plugins

    @classmethod
    def get_middlewares(cls):
        return [] # to override in plugins

    @classmethod
    def get_viewlets(cls):
        return [] # to override in plugins

    @classmethod
    def post_actions(cls):
        pass

    @classmethod
    def section_models(cls):
        return [] # to override in plugins

    @classmethod
    def section_register_hook(cls, site_related, model):
        pass

    @classmethod
    def get_model_admins(cls):
        return [] # to override in plugins

    @classmethod
    def get_perms(cls):
        return [] # to override in plugins

    @classmethod
    def hook_post_register(cls):
        pass

    @classmethod
    def get_notifications(cls):
        return [] # to override in plugins


def register_plugin(plugin_dir):
    from merengue.pluggable.models import RegisteredPlugin
    from merengue.pluggable.utils import get_plugin_config, validate_plugin
    plugin_config = get_plugin_config(plugin_dir)
    if plugin_config:
        validate_plugin(plugin_config)
        if not is_registered(plugin_config):
            register(plugin_config)
        plugin = RegisteredPlugin.objects.get_by_item(plugin_config)
        plugin.name = getattr(plugin_config, 'name')
        plugin.directory_name = plugin_dir
        plugin.description = getattr(plugin_config, 'description', '')
        plugin.version = getattr(plugin_config, 'version', '')
        plugin.required_apps = getattr(plugin_config, 'required_apps',
                                       None)
        plugin.required_plugins = getattr(plugin_config,
                                          'required_plugins',
                                          None)
        plugin.meta_info = {}
        if hasattr(plugin_config, 'screenshot'):
            plugin.meta_info['screenshot'] = plugin_config.screenshot
        plugin.meta_info['actions'] = []
        for action in plugin_config.get_actions():
            plugin.meta_info['actions'].append({'name': unicode(action.name), 'help_text': unicode(action.help_text)})
        plugin.meta_info['blocks'] = []
        for block in plugin_config.get_blocks():
            plugin.meta_info['blocks'].append({'name': unicode(block.name), 'help_text': unicode(block.help_text)})
        if plugin_config.get_model_admins():
            plugin.meta_info['has_own_admin'] = True
        else:
            plugin.meta_info['has_own_admin'] = False
        plugin.meta_info['middlewares'] = []
        for middleware in plugin_config.get_middlewares():
            plugin.meta_info['middlewares'].append(middleware)
        plugin.meta_info['section_models'] = []
        for model, admin in plugin_config.section_models():
            plugin.meta_info['section_models'].append({'name': unicode(model._meta.verbose_name)})
        plugin.meta_info['viewlets'] = []
        for viewlet in plugin_config.get_viewlets():
            plugin.meta_info['viewlets'].append({'name': unicode(viewlet.name), 'help_text': unicode(viewlet.help_text)})

        if "notification" in settings.INSTALLED_APPS:
            from notification.models import create_notice_type
            for notification in plugin_config.get_notifications():
                label, display, description = notification
                create_notice_type(label, display, description)

        plugin.save()
        return plugin
    return None


def enable_active_plugins():
    from merengue.pluggable.models import RegisteredPlugin
    from merengue.pluggable.utils import enable_plugin, get_plugin_module_name
    for plugin_registered in RegisteredPlugin.objects.actives():
        enable_plugin(get_plugin_module_name(plugin_registered.directory_name))


def register_all_plugins(verbose=False):
    from merengue.pluggable.utils import get_plugin_directories, get_plugin_config
    for plugin_dir in get_plugin_directories():
        if verbose:
            plugin_config = get_plugin_config(plugin_dir)
            if plugin_config:
                if not is_registered(plugin_config):
                    print 'Registering new plugin %s...' % plugin_dir
                else:
                    print 'Re-registering plugin %s...' % plugin_dir
            else:
                print 'Error walking to plugin %s.' % plugin_dir
        register_plugin(plugin_dir)


def active_default_plugins(*args, **kwargs):
    """ active default plugins and creates the portal menu in each language """
    # Only want to run this signal after all application was migrated, but
    # south have not a "post all migrations" signal.
    # The workaround is "collab" have to be the last application migrated
    if is_last_application(kwargs['app']):
        interactive = kwargs.get('interactive', None)
        # register required plugins
        for plugin_dir in settings.REQUIRED_PLUGINS:
            active_plugin_with_deps(plugin_dir)
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
    plugin = registered_plugin.get_registry_item_class()
    for dep in getattr(plugin, 'required_plugins', []):
        active_plugin_with_deps(dep)
    registered_plugin.installed = True
    registered_plugin.active = True
    registered_plugin.save()
    install_plugin(registered_plugin)


post_migrate.connect(active_default_plugins)
