from django.db import models
from django.db.models import signals
from django.db.models.loading import load_app
from django.utils.translation import ugettext_lazy as _

from pluginregistry import (are_installed_models, install_models,
                            get_plugin_module_name, add_to_installed_apps,
                            enable_plugin, disable_plugin)
from pluginregistry.managers import PluginManager


class Plugin(models.Model):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    version = models.CharField(_('version'), max_length=25)
    installed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    directory_name = models.CharField(_('directory name'), max_length=100)

    objects = PluginManager()

    def __unicode__(self):
        return self.name


def install_plugin(sender, instance, **kwargs):
    app_name = get_plugin_module_name(instance.directory_name)
    if instance.installed:
        app_mod = load_app(app_name)
        # Needed update installed apps in order to get SQL command from plugin
        add_to_installed_apps(app_name)
        if not are_installed_models(app_mod):
            install_models(app_mod)
            # Force instance saving after connection closes.
            instance.save()
        if instance.active:
            enable_plugin(app_name)
        else:
            disable_plugin(app_name)

signals.post_save.connect(install_plugin, sender=Plugin)
