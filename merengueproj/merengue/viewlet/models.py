from django.db import models

from merengue.registry.managers import RegisteredItemManager
from merengue.registry.models import RegisteredItem


class RegisteredViewlet(RegisteredItem):
    name = models.CharField(max_length=100)

    objects = RegisteredItemManager()

    def __unicode__(self):
        return u'%s (%s)' % (self.get_registry_item_class().label, self.name)
