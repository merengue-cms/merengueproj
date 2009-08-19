from django.db import models


class RegisteredItemManager(models.Manager):

    def get_by_item(self, item_class):
        """ obtain registered item passing by param a RegistrableItem """
        return self.get_query_set().get(
            module=item_class.get_module(),
            class_name=item_class.get_class_name(),
        )
