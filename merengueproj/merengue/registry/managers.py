from django.db import models
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist


class RegisteredItemQuerySet(QuerySet):

    def all(self):
        return self.filter(broken=False)

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

    def with_brokens(self):
        return self.filter()


class RegisteredItemManager(models.Manager):
    """ Registered item manager """

    def get_query_set(self):
        return RegisteredItemQuerySet(self.model)

    def with_brokens(self):
        return self.get_query_set().with_brokens()

    def actives(self, ordered=False):
        """ Retrieves active items for site """
        return self.get_query_set().actives()

    def inactives(self, ordered=False):
        """ Retrieves inactive items for site """
        return self.get_query_set().inactives()

    def get_by_item(self, item_class):
        """ obtain registered item passing by param a RegistrableItem """
        for registered_item in self.all():
            if registered_item.module == item_class.get_module() and \
               registered_item.class_name == item_class.get_class_name():
                return registered_item
        raise ObjectDoesNotExist
