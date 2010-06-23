# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from merengue.pluggable.utils import (install_plugin, get_plugins_dir,
                                      get_plugin_module_name, disable_plugin)
from merengue.pluggable.managers import PluginManager
from merengue.registry.dbfields import RequiredPluginsField, RequiredAppsField
from merengue.registry.models import RegisteredItem


class RegisteredPlugin(RegisteredItem):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    version = models.CharField(_('version'), max_length=25)
    required_apps = RequiredAppsField()
    required_plugins = RequiredPluginsField()
    installed = models.BooleanField(default=False)
    directory_name = models.CharField(_('directory name'), max_length=100,
                                      unique=True)

    class Meta:
        db_table = 'plugins_registeredplugin'

    objects = PluginManager()

    def __unicode__(self):
        return self.name

    def get_path(self):
        """Full absolute path to the plugin root, including
        settings.PLUGINS_DIR."""
        basedir = settings.BASEDIR
        plugins_dir = get_plugins_dir()
        return os.path.join(basedir, plugins_dir, self.directory_name)


def install_plugin_signal(sender, instance, **kwargs):
    if not getattr(instance, 'id', None) and getattr(instance, 'pk', None):
        instance = instance._default_manager.get(pk=instance.pk)
    if instance.installed and instance.directory_name and not instance.broken:
        app_name = get_plugin_module_name(instance.directory_name)
        install_plugin(instance, app_name)
    elif not instance.active and instance.directory_name: # Change this line will be fixes in #542
        disable_plugin(get_plugin_module_name(instance.directory_name))
signals.post_save.connect(install_plugin_signal, sender=RegisteredPlugin)
