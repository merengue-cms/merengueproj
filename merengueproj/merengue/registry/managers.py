from django.db import models


class RegisteredItemManager(models.Manager):

    def actives(self):
        """ Retrieves active items for site """
        return super(RegisteredItemManager, self).get_query_set().filter(active=True)

    def inactives(self):
        """ Retrieves inactive items for site """
        return super(RegisteredItemManager, self).get_query_set().exclude(active=True)

    def get_by_item(self, item_class):
        """ obtain registered item passing by param a RegistrableItem """
        return self.get_query_set().get(
            module=item_class.get_module(),
            class_name=item_class.get_class_name(),
        )
