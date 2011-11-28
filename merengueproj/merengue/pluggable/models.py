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

import os

from django.conf import settings
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from south.modelsinspector import add_introspection_rules

from merengue.base.dbfields import JSONField
from merengue.perms import utils as perms_api
from merengue.pluggable.managers import PluginManager
from merengue.pluggable.dbfields import RequiredPluginsField, RequiredAppsField
from merengue.registry.models import RegisteredItem


class RegisteredPlugin(RegisteredItem):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), default='')
    version = models.CharField(_('version'), max_length=25)
    required_apps = RequiredAppsField()
    required_plugins = RequiredPluginsField()
    installed = models.BooleanField(_('installed'), default=False)
    directory_name = models.CharField(_('directory name'), max_length=100,
                                      unique=True)
    meta_info = JSONField(null=True)

    @property
    def screenshot(self):
        if self.meta_info and 'screenshot' in self.meta_info:
            return os.path.join(settings.MEDIA_URL, self.directory_name,
                                self.meta_info['screenshot'])
        return None

    class Meta:
        db_table = 'plugins_registeredplugin'
        verbose_name = _('registered plugin')
        verbose_name_plural = _('registered plugins')
        ordering = ('order', )

    objects = PluginManager()

    def get_plugin_config(self):
        from merengue.pluggable.utils import get_plugin_config
        return get_plugin_config(self.directory_name)

    def __unicode__(self):
        return self.name

    def can_delete(self, user):
        # user only can delete broken objects
        return perms_api.can_manage_site(user) and self.broken

    def get_path(self):
        """Full absolute path to the plugin root, including
        settings.PLUGINS_DIR."""
        from merengue.pluggable.utils import get_plugins_dir
        basedir = settings.BASEDIR
        plugins_dir = get_plugins_dir()
        return os.path.join(basedir, plugins_dir, self.directory_name)


def save_plugin_signal(sender, instance, **kwargs):
    from merengue.pluggable.utils import (get_plugin_module_name,
                                          enable_plugin,
                                          disable_plugin)
    app_name = get_plugin_module_name(instance.directory_name)
    if not getattr(instance, 'id', None) and getattr(instance, 'pk', None):
        instance = instance._default_manager.get(pk=instance.pk)
    if instance.installed and instance.active and instance.directory_name and not instance.broken:
        enable_plugin(app_name)
    elif not instance.active and instance.directory_name:
        try:
            disable_plugin(app_name)
        except ImportError:
            if instance.broken:
                pass  # the plugin is broken
            else:
                raise
signals.post_save.connect(save_plugin_signal, sender=RegisteredPlugin)

# ----- adding south rules to help introspection -----

rules = [
  (
    (RequiredAppsField, RequiredPluginsField),
    [],
    {},
  ),
]

rules_jsonfield = [
  (
    (JSONField, ),
    [],
    {},
  ),
]

add_introspection_rules(rules, ["^merengue\.pluggable"])
add_introspection_rules(rules_jsonfield, ["^merengue\.base"])
