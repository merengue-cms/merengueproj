import os

from django.conf import settings
from django.db import models
from django.db.models import signals
from django.db.models.loading import load_app
from django.utils.translation import ugettext_lazy as _

from merengue.plugins.utils import (add_to_installed_apps,
                                    are_installed_models,
                                    disable_plugin, enable_plugin,
                                    install_models, get_plugins_dir,
                                    get_plugin_module_name,
                                    reload_app_directories_template_loader)
from merengue.plugins.managers import PluginManager
from merengue.registry.dbfields import RequiredPluginsField, RequiredAppsField
from merengue.registry.models import RegisteredItem


class RegisteredPlugin(RegisteredItem):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    version = models.CharField(_('version'), max_length=25)
    required_apps = RequiredAppsField()
    required_plugins = RequiredPluginsField()
    installed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    directory_name = models.CharField(_('directory name'), max_length=100,
                                      unique=True)

    objects = PluginManager()

    def __unicode__(self):
        return self.name

    def get_path(self):
        """Full absolute path to the plugin root, including
        settings.PLUGINS_DIR."""
        basedir = settings.BASEDIR
        plugins_dir = get_plugins_dir()
        return os.path.join(basedir, plugins_dir, self.directory_name)


def install_plugin(sender, instance, **kwargs):
    app_name = get_plugin_module_name(instance.directory_name)
    if instance.installed:
        app_mod = load_app(app_name)
        # Needed update installed apps in order
        # to get SQL command from merengue.plugin
        add_to_installed_apps(app_name)
        if not are_installed_models(app_mod):
            install_models(app_mod)
            # Force instance saving after connection closes.
            instance.save()
        if instance.active:
            enable_plugin(app_name)
        else:
            disable_plugin(app_name)
        # app_directories template loader loads app_template_dirs in
        # compile time, so we have to load it again.
        reload_app_directories_template_loader()

signals.post_save.connect(install_plugin, sender=RegisteredPlugin)
