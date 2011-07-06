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

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseCategory

from transmeta import TransMeta
from stdimage import StdImageField


class StandingOutCategory(BaseCategory):

    context_variable = models.CharField(verbose_name=_('context variable'), max_length=200)

    class Meta:
        verbose_name = _('standingout category')
        verbose_name_plural = _('standingout categories')


class StandingOut(models.Model):

    __metaclass__ = TransMeta

    title = models.CharField(_('title'), max_length=200, blank=True, null=True)
    short_description = models.TextField(_('short description'), blank=True, null=True)
    image = StdImageField(
        _('image'),
        help_text=_('If you don\'t specify any image then the first photo (if any) associated to the content will be shown'),
        upload_to='standingout',
        thumbnail_size=(350, 240),
        null=True,
        blank=True,
        )
    obj_content_type = models.ForeignKey(ContentType, verbose_name=_('obj content type'),
                                         related_name='standingout_objects', null=True, blank=True)
    obj_id = models.PositiveIntegerField(_('object id'), db_index=True, null=True, blank=True)
    obj = generic.GenericForeignKey('obj_content_type', 'obj_id')

    url = models.CharField(
        verbose_name=_('url'), max_length=200, null=True, blank=True,
        help_text=_('The absolute urls have to write complety: Protocol, domain, query'),
    )

    related_content_type = models.ForeignKey(ContentType, verbose_name=_('related content type'), null=True, blank=True,
                                             related_name='standingout_relateds')
    related_id = models.PositiveIntegerField(_('related object id'), db_index=True, null=True, blank=True)
    related = generic.GenericForeignKey('related_content_type', 'related_id')

    standing_out_category = models.ForeignKey(StandingOutCategory, verbose_name=_('standing out category'),
                                         null=True, blank=True)
    # The order goes from 0 to n - 1
    order = models.IntegerField(_("Order"), blank=True, null=True)

    class Meta:
        ordering = ('-order', )
        translate = ('title', 'short_description')
        verbose_name = _('standing out')
        verbose_name_plural = _('standing outs')

    @property
    def name(self):
        return self.title or self.obj and unicode(self.obj) or self.target_name()

    @property
    def description(self):
        return self.short_description or getattr(self.obj, 'description', '')

    def has_description(self):
        return True

    @property
    def main_image(self):
        return self.obj.main_image

    def get_absolute_url(self):
        url = None
        if hasattr(self.obj, 'get_absolute_url'):
            url = self.obj.get_absolute_url()
        else:
            url = self.url
        return url

    def target_name(self):
        target = ''
        if self.obj:
            target = unicode(self.obj)
        elif self.url:
            target = self.url
        return target

    def __unicode__(self):
        if self.title:
            return self.title
        elif self.obj:
            return unicode(self.obj)
        return 'without content'
