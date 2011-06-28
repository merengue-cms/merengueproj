# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

import traceback

from django.db import models
from django.db.models import signals
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from south.modelsinspector import add_introspection_rules

from merengue.perms import utils as perms_api
from merengue.registry.dbfields import ConfigField
from merengue.registry.managers import RegisteredItemManager, clear_lookup_cache


class RegisteredItem(models.Model):
    class_name = models.CharField(_('class name'), max_length=100, db_index=True)
    module = models.CharField(_('module'), max_length=200, db_index=True)
    category = models.CharField(_('category'), max_length=100, db_index=True)
    active = models.BooleanField(_('active'), default=False)
    broken = models.BooleanField(_('broken'), default=False, editable=False)
    order = models.IntegerField(_("Order"), blank=True, null=True)
    traceback = models.TextField(_("Error traceback"), default='', editable=False,
                                 help_text=_("Error traceback on broken item"))
    config = ConfigField(_('Configuration'))

    objects = RegisteredItemManager()

    class Meta:
        verbose_name = _('registered item')
        verbose_name_plural = _('registered items')
        ordering = ('order', )

    def __unicode__(self):
        return self.class_name

    def save(self, *args, **kwargs):
        if not self.id and not self.order:
            max_order = RegisteredItem.objects.aggregate(models.Max('order'))['order__max']
            self.order = (max_order and max_order + 1) or 0
        super(RegisteredItem, self).save(*args, **kwargs)

    def set_default_config(self, item_class):
        if not self.config:
            self.config = {}
        for param in item_class.config_params:
            if param.has_default():
                self.config[param.name] = param.default
        self.save()

    def get_registry_item(self):
        module = import_module(self.module)
        item_class = getattr(module, self.class_name)
        return item_class(self)

    def has_config(self):
        return bool(self.get_registry_item().config_params)

    def get_config(self):
        return self.config

    def activate(self, commit=True):
        if not self.active:
            self.active = True
            if commit:
                self.save()

    def can_delete(self, user):
        return perms_api.can_manage_site(user)

    def deactivate(self, commit=True):
        if self.active:
            self.active = False
            if commit:
                self.save()

    def set_traceback(self, exc_type, exc_value, tb):
        formatted_exception = []
        formatted_exception.append('Exception Type: %s' % exc_type)
        formatted_exception.append('Exception Value: %s' % exc_value)
        formatted_exception.append('Traceback:')
        traceback_frames = traceback.extract_tb(tb)
        formatted_exception += traceback.format_list(traceback_frames)
        self.traceback = '<br/>'.join(formatted_exception)


# ----- signals handling -----

def post_save_handler(sender, instance, **kwargs):
    if isinstance(instance, RegisteredItem):
        clear_lookup_cache()

signals.post_save.connect(post_save_handler)


# ----- adding south rules to help introspection -----

rules = [
  (
    (ConfigField, ),
    [],
    {},
  ),
]

add_introspection_rules(rules, ["^merengue\.registry"])
