from django.db import models
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _

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


class BaseSubscription(models.Model):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('e-mail address'))
    phone = models.CharField(_('phone'), max_length=30)
    suggestions = models.TextField(_('comments or suggestions'), null=True, blank=True)

    class Meta:
        verbose_name = _('base subscription')
        verbose_name_plural = _('base subscriptions')

    @classmethod
    def class_form(cls):
        return modelform_factory(cls)
