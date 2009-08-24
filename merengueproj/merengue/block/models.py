from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.registry.managers import RegisteredItemManager
from merengue.registry.models import RegisteredItem


PLACES = (('leftsidebar', _('Left sidebar')),
          ('rightsidebar', _('Right sidebar')),
          ('content', _('After content')))


class RegisteredBlock(RegisteredItem):
    name = models.CharField(max_length=100)
    placed_at = models.CharField(max_length=100, choices=PLACES)

    objects = RegisteredItemManager()

    def __unicode__(self):
        return self.name
