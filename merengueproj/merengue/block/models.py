from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.registry.managers import RegisteredItemManager
from merengue.registry.models import RegisteredItem


PLACES = (('all', _('All')),
          ('leftsidebar', _('Left sidebar')),
          ('rightsidebar', _('Right sidebar')),
          ('beforecontent', _('Before content body')),
          ('homepage', _('Home page')),
          ('aftercontent', _('After content body')),
          ('header', _('Header')),
          ('footer', _('Footer')))


class RegisteredBlock(RegisteredItem):
    name = models.CharField(max_length=100)
    placed_at = models.CharField(max_length=100, choices=PLACES)

    objects = RegisteredItemManager()

    def print_block(self, placed_at):
        if self.placed_at == 'all' or placed_at == self.placed_at:
            return True
        return False

    def __unicode__(self):
        return self.name
