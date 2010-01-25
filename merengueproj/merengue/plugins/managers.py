from merengue.registry.managers import RegisteredItemManager
from merengue.registry.models import RegisteredItem


class PluginManager(RegisteredItemManager):
    """ Plugin manager """

    def flush_cache(self):
        super(PluginManager, self).flush_cache()
        # we have to flush also RegisteredItem cache
        # because is half-shared with this cache
        # see ticket #266
        RegisteredItem.objects.flush_cache()
