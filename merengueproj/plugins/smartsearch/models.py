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

from autoreports.models import BaseReport
from merengue.collection.models import Collection


class Searcher(BaseReport):

    collections = models.ManyToManyField(
        Collection,
        verbose_name=_(u'Collections'),
    )

    def get_redirect_wizard(self, report=None):
        return '../%s/' % self.id

    class Meta:
        verbose_name = _('searcher')
        verbose_name_plural = _('searchers')
