from django.db import models
from django.db.models import signals
from django.db.models.loading import load_app
from django.contrib.admin.sites import AlreadyRegistered, NotRegistered
from django.utils.translation import ugettext_lazy as _

from pluginregistry import (are_installed_models, install_models,
                            get_plugins_dir, update_installed_apps)
from pluginregistry.managers import PluginManager

from merengue.admin import register_app, unregister_app


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
    plugins_dir = get_plugins_dir()
    app_name = '%s.%s' % (plugins_dir, instance.directory_name)
    if instance.installed:
        app_mod = load_app(app_name)
        update_installed_apps(app_name)
        if not are_installed_models(app_mod):
            install_models(app_mod)
            # Force instance saving after connection closes.
            instance.save()
        if instance.active:
            try:
                register_app(app_name)
            except AlreadyRegistered:
                pass
        else:
            try:
                unregister_app(app_name)
            except NotRegistered:
                pass


signals.post_save.connect(install_plugin, sender=Plugin)
