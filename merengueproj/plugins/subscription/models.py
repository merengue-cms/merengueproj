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

from django.db import models
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from merengue.base.models import BaseContent
from plugins.subscription.managers import SubscribableManager


class Subscribable(models.Model):
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)
    content = models.ForeignKey(BaseContent,
                                verbose_name=_('content'),
                                db_index=True)
    class_name = models.CharField(_('Type of Subscription'),
                                  max_length=200)

    objects = SubscribableManager()

    class Meta:
        verbose_name = _('subscribable')
        verbose_name_plural = _('subscribables')

    def __unicode__(self):
        return ugettext('Subscribable for %s') % self.content


class BaseSubscription(models.Model):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('e-mail address'))
    phone = models.CharField(_('phone'), max_length=30)
    suggestions = models.TextField(_('comments or suggestions'), null=True, blank=True)
    subscribable = models.ForeignKey(Subscribable, verbose_name=_('subscribable'), editable=False)

    class Meta:
        verbose_name = _('base subscription')
        verbose_name_plural = _('base subscriptions')

    def __unicode__(self):
        return ugettext('Subscription of %s') % self.email

    @classmethod
    def class_form(cls):
        form = modelform_factory(cls)
        # subscribable object is automatically defined
        del form.base_fields['subscribable']
        return form
