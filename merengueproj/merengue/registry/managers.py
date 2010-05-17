from django.db import models
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist

from cmsutils.utils import QuerySetWrapper


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

    def cleaning_brokens(self):
        """
        Returns registered items cleaning broken ones (not existing in FS)
        If you use this method you will prevent errors with python modules
        deleted from file system.
        """
        from merengue.registry import is_broken
        from merengue.plugin.utils import is_plugin_broken, get_plugin_module_name
        cleaned_items = []
        for registered_item in self.with_brokens():
            plugin_name = get_plugin_module_name(registered_item.directory_name)
            if is_broken(registered_item) or is_plugin_broken(plugin_name):
                registered_item.broken = True
                registered_item.save()
            else:
                cleaned_items.append(registered_item)
                if registered_item.broken:
                    # in past was broken but now is ok
                    registered_item.broken = False
                    registered_item.save()
        return QuerySetWrapper(cleaned_items)


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
