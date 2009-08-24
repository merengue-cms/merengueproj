from django.db import models


class ThemeManager(models.Manager):
    """ Theme manager """

    def active(self):
        """ Retrieves active theme for site """
        return super(ThemeManager, self).get_query_set().get(active=True)
