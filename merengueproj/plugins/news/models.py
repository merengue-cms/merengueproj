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
from django.db.models import permalink
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _

from cmsutils.cache import CachingManager

from merengue.base.models import BaseContent, BaseCategory
from plugins.news.managers import NewsItemManager


class NewsCategory(BaseCategory):

    class Meta:
        verbose_name = _('news category')
        verbose_name_plural = _('news categories')

    objects = CachingManager(cache_object_retrieval=True)


class NewsItem(BaseContent):

    publish_date = models.DateTimeField(blank=True, null=True, db_index=True)
    expire_date = models.DateTimeField(blank=True, null=True, db_index=True)
    categories = models.ManyToManyField(NewsCategory,
                                        verbose_name=_('category'),
                                        blank=True, null=True, db_index=True)
    body = models.TextField(_('body'))

    objects = NewsItemManager()

    class Meta:
        translate = ('body', )
        content_view_template = 'news/newsitem_view.html'
        ordering = ('-publish_date', '-id')

    def _public_link_simply(self):
        return ('newsitem_view', [self.slug])

    @permalink
    def public_link(self):
        section = self.get_main_section()
        if section is None:
            return self._public_link_simply()
        else:
            # go to news item inside section which created it
            return section.real_instance.content_public_link(section, self)


def set_publish_date(sender, instance, **kwargs):
    if instance.status == 'published' and not instance.publish_date:
        instance.publish_date = datetime.datetime.now()

pre_save.connect(set_publish_date, sender=NewsItem)
