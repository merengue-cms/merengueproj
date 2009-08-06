from django.db import models


class PluginManager(models.Manager):
    """ Theme manager """

    def active(self):
        """ Retrieves active theme for site """
        return super(PluginManager, self).get_query_set().get(active=True)
