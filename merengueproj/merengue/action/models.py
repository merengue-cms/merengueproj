from django.db import models

from merengue.registry.models import RegisteredItem


class RegisteredAction(RegisteredItem):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name
