from merengue.registry.managers import RegisteredItemManager


class PluginManager(RegisteredItemManager):
    """ Plugin manager """

    def actives(self):
        """ Retrieves active plugins for site """
        return super(PluginManager, self).get_query_set().filter(active=True)

    def inactives(self):
        """ Retrieves inactive plugins for site """
        return super(PluginManager, self).get_query_set().exclude(active=True)
