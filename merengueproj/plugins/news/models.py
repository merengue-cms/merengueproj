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
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent, BaseCategory
from plugins.news.managers import NewsItemManager


class NewsCategory(BaseCategory):

    class Meta:
        verbose_name = _('news category')
        verbose_name_plural = _('news categories')


class NewsItem(BaseContent):

    publish_date = models.DateTimeField(verbose_name=_('publish date'),
                                        blank=True,
                                        null=True,
                                        db_index=True)
    expire_date = models.DateTimeField(verbose_name=_('expire date'),
                                       blank=True,
                                       null=True,
                                       db_index=True)
    categories = models.ManyToManyField(NewsCategory,
                                        verbose_name=_('category'),
                                        blank=True, null=True, db_index=True)
    body = models.TextField(_('body'))

    objects = NewsItemManager()

    class Meta:
        translate = ('body', )
        content_view_template = 'news/newsitem_view.html'
        ordering = ('-publish_date', '-id')
        verbose_name = _('news item')
        verbose_name_plural = _('news')
        check_slug_uniqueness = True

    def _public_link_without_section(self):
        return ('newsitem_view', [self.slug])


def set_publish_date(sender, instance, **kwargs):
    if instance.status == 'published' and not instance.publish_date:
        instance.publish_date = datetime.datetime.now()

pre_save.connect(set_publish_date, sender=NewsItem)
