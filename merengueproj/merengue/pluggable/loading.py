import threading

__all__ = ('plugins_loaded', )


class PluginState(object):
    """
    A cache that stores actives plugins.
    """
    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    __shared_state = dict(
        loaded = False,
        write_lock = threading.RLock(),
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
            from merengue.pluggable.utils import (enable_plugin,
                                                  get_plugin_module_name)
            from merengue.pluggable.models import RegisteredPlugin
            # enable active plugins
            active_plugins = RegisteredPlugin.objects.actives()
            plugin_names = [get_plugin_module_name(p.directory_name)
                            for p in active_plugins]
            for plugin_name in plugin_names:
                enable_plugin(plugin_name, register=True)
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
