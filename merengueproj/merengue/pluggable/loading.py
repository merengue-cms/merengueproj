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

import threading

__all__ = ('plugins_loaded', )


class PluginState(object):
    """
    A cache that stores actives plugins.
    """
    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    __shared_state = dict(
        loaded=False,
        write_lock=threading.RLock(),
    )

    def __init__(self):
        self.__dict__ = self.__shared_state

    def load_plugins(self):
        """
        Enable plugins and set "loaded" attribute. This method is threadsafe, in the
        sense that every caller will see the same state upon return, and if the
        cache is already initialised, it does no work.
        """
        if self.loaded:
            return
        self.write_lock.acquire()
        try:
            if self.loaded:
                return
            from merengue.registry import invalidate_registereditem
            from merengue.pluggable.utils import (enable_plugin,
                                                  get_plugin_module_name,
                                                  reload_models_cache)
            from merengue.pluggable.models import RegisteredPlugin
            # enable active plugins
            active_plugins = RegisteredPlugin.objects.actives()
            plugin_names = [get_plugin_module_name(p.directory_name)
                            for p in active_plugins]
            for plugin_name in plugin_names:
                enable_plugin(plugin_name, register=True)
            # invalidate any existing cache
            invalidate_registereditem()
            # reload models cache. needed because new plugins could bring new models
            reload_models_cache()
            self.loaded = True
        finally:
            self.write_lock.release()

    def plugins_loaded(self):
        """
        Returns true if the plugins cache is fully populated.
        """
        return self.loaded

plugins_state = PluginState()

plugins_loaded = plugins_state.plugins_loaded
load_plugins = plugins_state.load_plugins
