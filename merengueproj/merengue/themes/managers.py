from cmsutils.cache import CachingManager


class ThemeManager(CachingManager):
    """ Theme manager """

    def active(self):
        """ Retrieves active theme for site """
        return self.cache().get(active=True)
