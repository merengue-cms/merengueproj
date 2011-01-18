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

import datetime

from django.db import models
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
        ordering = ('-publish_date', )

    def _public_link_without_section(self):
        return ('event_view', [self.slug])

    def __unicode__(self):
        return self.name or u''

    def visible(self):
        return self.end > datetime.datetime.now()
