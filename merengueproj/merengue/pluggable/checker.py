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

from merengue.pluggable import register_all_plugins
from merengue.pluggable.exceptions import BrokenPlugin
from merengue.pluggable.loading import load_plugins
from merengue.pluggable.utils import (check_plugin_broken, register_dummy_plugin,
                                      reload_models_cache)


def check_plugins(force_detect=False, force_broken_detect=False):
    """ check plugins found in file system and compare with registered
        one in database """
    # all process will be in a unique transaction, we don't want to get
    # self committed

    if settings.DETECT_NEW_PLUGINS or force_detect:
        register_all_plugins()

    if settings.DETECT_BROKEN_PLUGINS or force_broken_detect:
        mark_broken_plugins()

    # finally, we reload active plugins
    load_plugins()


def mark_broken_plugins():
    """
    Mark broken plugins (i.e. not existing in FS). This will prevent errors
    with python modules deleted from file system or broken modules.
    """
    from merengue.pluggable.models import RegisteredPlugin
    try:
        for registered_item in RegisteredPlugin.objects.inactives():
            plugin_name = registered_item.directory_name
            mark_broken_plugin(plugin_name, registered_item)
    finally:
        reload_models_cache()


def mark_broken_plugin(plugin_name, registered_plugin=None):
    if registered_plugin is None:
        registered_plugin = register_dummy_plugin(plugin_name)
    try:
        check_plugin_broken(plugin_name)
    except BrokenPlugin, e:
        registered_plugin.broken = True
        registered_plugin.set_traceback(e.exc_type, e.exc_value, e.traceback)
        registered_plugin.save()
    else:
        if registered_plugin.broken:
            # in past was broken but now is ok
            registered_plugin.broken = False
            registered_plugin.save()
