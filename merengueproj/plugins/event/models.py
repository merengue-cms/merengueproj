import datetime

from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent, BaseCategory

from plugins.event.managers import EventManager


class Category(BaseCategory):
    """ Event category (deportes nauticos, toros, flamenco...) """

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')


class Event(BaseContent):
    """ An event """
    publish_date = models.DateTimeField(blank=True, null=True, db_index=True,
                                        editable=False)
    expire_date = models.DateTimeField(blank=True, null=True, db_index=True)
    start = models.DateTimeField(_('Start date'), null=True, editable=True,
                                db_index=True)
    end = models.DateTimeField(_('End date'), null=True, editable=True,
                               db_index=True)
    categories = models.ManyToManyField(Category,
                                      verbose_name=_('category'),
                                      blank=True, null=True, db_index=True)

    objects = EventManager()

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    @permalink
    def public_link(self):
        return ('plugins.event.views.event_view', [self.slug])

    def __unicode__(self):
        return self.name or u''

    def visible(self):
        return self.end > datetime.datetime.now()
