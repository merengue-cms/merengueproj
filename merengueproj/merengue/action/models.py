from django.db import models

from merengue.registry.managers import RegisteredItemManager
from merengue.registry.models import RegisteredItem


class RegisteredAction(RegisteredItem):
    name = models.CharField(max_length=100)

    objects = RegisteredItemManager()

    def __unicode__(self):
        return self.name
