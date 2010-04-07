from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class RegisteredItemManager(models.Manager):

    def filter(self, *args, **kwargs):
        return super(RegisteredItemManager, self).filter(*args, **kwargs)

    def actives(self, ordered=False):
        """ Retrieves active items for site """
        if not ordered:
            return self.filter(active=True)
        else:
            return self.filter(active=True).order_by('order')

    def inactives(self, ordered=False):
        """ Retrieves inactive items for site """
        if not ordered:
            return self.exclude(active=True)
        else:
            return self.exclude(active=True).order_by('order')

    def get_by_item(self, item_class):
        """ obtain registered item passing by param a RegistrableItem """
        for registered_item in self.all():
            if registered_item.module == item_class.get_module() and \
               registered_item.class_name == item_class.get_class_name():
                return registered_item
        raise ObjectDoesNotExist
