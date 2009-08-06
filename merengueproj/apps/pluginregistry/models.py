from django.conf import settings
from django.core.management.color import color_style
from django.core.management.sql import sql_all
from django.db import models
from django.db.models import signals
from django.db.models.loading import load_app
from django.utils.translation import ugettext_lazy as _

from pluginregistry import get_plugins_dir
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


def update_installed_apps(sender, instance, **kwargs):
    if instance.installed:
        plugins_dir = get_plugins_dir()
        app_name = instance.directory_name
        app_to_load = '%s.%s' % (plugins_dir, app_name)
        settings.INSTALLED_APPS = tuple(
            list(settings.INSTALLED_APPS) + [app_to_load],
        )
        app_mod = load_app(app_to_load)
        style = color_style()
        print " ".join(sql_all(app_mod, style))
        if instance.active:
            pass

signals.post_save.connect(update_installed_apps, sender=Plugin)
