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


class CustomMeta(models.Model):

    url_regexp = models.CharField(
        verbose_name=_('url regular expression'),
        max_length=255,
        blank=False,
        null=False,
        )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=255,
        blank=True,
        null=True,
        )
    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
        )
    keywords = models.TextField(
        verbose_name=_('keywords'),
        help_text=_('input one keyword per row'),
        blank=True,
        null=True,
        )

    class Meta:
        verbose_name = _('Custom Meta Information')
        verbose_name_plural = _('Custon Meta Informations')

    def __unicode__(self):
        return self.url_regexp

    def get_keywords(self):
        if self.keywords:
            for i in self.keywords.split('\n'):
                keyword = i.strip()
                if keyword:
                    yield keyword
