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
import sys
import subprocess

from django.conf import settings

from merengue.pluggable.exceptions import BrokenPlugin
from merengue.pluggable.loading import load_plugins
from merengue.pluggable.utils import check_plugin_broken, get_plugin_module_name


def check_plugins():
    """ check plugins found in file system and compare with registered
        one in database """
    # all process will be in a unique transaction, we don't want to get
    # self committed
    process_environ = {
        'PYTHONPATH': ':'.join(sys.path),
        'DJANGO_SETTINGS_MODULE': os.environ['DJANGO_SETTINGS_MODULE'],
    }

    sys_executable = settings.SYS_EXECUTABLE or sys.executable

    if settings.DETECT_NEW_PLUGINS:
        # now look for all plugins in filesystem and register them
        # we have to launch other process because broken plugin detection
        # tries to validate models and this register non valid meta information
        # (fields, m2m, etc.)
        process = subprocess.Popen(
            [sys_executable, settings.MANAGE_FILE, "register_new_plugins"],
            cwd=settings.BASEDIR, env=process_environ,
        )
        process.wait()

    if settings.DETECT_BROKEN_PLUGINS:
        # we have to launch other process because broken plugin detection
        # tries to validate models and this register non valid meta information
        # (fields, m2m, etc.)
        process = subprocess.Popen(
            [sys_executable, settings.MANAGE_FILE, "mark_broken_plugins"],
            cwd=settings.BASEDIR, env=process_environ,
        )
        process.wait()

    # finally, we reload active plugins
    load_plugins()


def mark_broken_plugins():
    """
    Mark broken plugins (i.e. not existing in FS). This will prevent errors
    with python modules deleted from file system or broken modules.
    """
    from merengue.pluggable.models import RegisteredPlugin
    cleaned_items = []
    for registered_item in RegisteredPlugin.objects.inactives():
        plugin_name = get_plugin_module_name(registered_item.directory_name)
        try:
            check_plugin_broken(plugin_name)
        except BrokenPlugin, e:
            registered_item.broken = True
            registered_item.set_traceback(e.exc_type, e.exc_value, e.traceback)
            registered_item.save()
        else:
            cleaned_items.append(registered_item)
            if registered_item.broken:
                # in past was broken but now is ok
                registered_item.broken = False
                registered_item.save()
