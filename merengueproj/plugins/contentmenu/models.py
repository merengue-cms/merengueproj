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

from merengue.base.models import BaseContent


class ContentGroup(models.Model):

    name = models.CharField(
        verbose_name=_('identifier name of this content group'),
        max_length=200)
    contents = models.ManyToManyField(
        BaseContent, verbose_name=_('contents related to the group'))

    class Meta:
        verbose_name = _('Content Group')
        verbose_name_plural = _('Content Groups')

    def __unicode__(self):
        return self.name
