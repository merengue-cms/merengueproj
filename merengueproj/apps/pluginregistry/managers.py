from django.db import models


class PluginManager(models.Manager):
    """ Plugin manager """

    def actives(self):
        """ Retrieves active plugins for site """
        return super(PluginManager, self).get_query_set().filter(active=True)
