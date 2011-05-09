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
from django.utils.translation import ugettext_lazy as _

from merengue.base.managers import BaseContentManager
from merengue.base.models import BaseCategory, BaseContent


class LinkCategory(BaseCategory):

    class Meta:
        verbose_name = _('link category')
        verbose_name_plural = _('link categories')


class Link(BaseContent):

    url_link = models.URLField(verbose_name=_('Url Link'))
    portal_name = models.CharField(verbose_name=_('Portal name'), max_length=250, blank=True, null=True)
    categories = models.ManyToManyField(LinkCategory,
                                        verbose_name=_('category'),
                                        blank=True, null=True, db_index=True)
    objects = BaseContentManager()

    class Meta:
        verbose_name = _('link')
        verbose_name_plural = _('links')
        check_slug_uniqueness = True

    def _public_link_without_section(self):
        return ('link_view', [self.slug])
