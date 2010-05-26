from merengue.registry.managers import RegisteredItemManager

from cmsutils.utils import QuerySetWrapper


class PluginManager(RegisteredItemManager):
    """ Plugin manager """

    def cleaning_brokens(self):
        """
        Returns registered plugin cleaning broken ones (i.e. not existing in FS)
        If you use this method you will prevent errors with python modules
        deleted from file system or broken modules.
        """
        from merengue.pluggable import is_broken
        cleaned_items = []
        for registered_item in self.with_brokens():
            if is_broken(registered_item):
                registered_item.broken = True
                registered_item.save()
            else:
                cleaned_items.append(registered_item)
                if registered_item.broken:
                    # in past was broken but now is ok
                    registered_item.broken = False
                    registered_item.save()
        return QuerySetWrapper(cleaned_items)
