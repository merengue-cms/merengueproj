from django.core.exceptions import ObjectDoesNotExist

from cmsutils.cache import CachingManager


class RegisteredItemManager(CachingManager):

    def filter(self, *args, **kwargs):
        return super(RegisteredItemManager, self).filter(*args, **kwargs)

    def actives(self):
        """ Retrieves active items for site """
        return self.cache().filter(active=True)

    def inactives(self):
        """ Retrieves inactive items for site """
        return self.cache().exclude(active=True)

    def get_by_item(self, item_class):
        """ obtain registered item passing by param a RegistrableItem """
        for registered_item in self.cache():
            # note: we do not use get to use cache from caching manager
            if registered_item.module == item_class.get_module() and \
               registered_item.class_name == item_class.get_class_name():
                return registered_item
        raise ObjectDoesNotExist
