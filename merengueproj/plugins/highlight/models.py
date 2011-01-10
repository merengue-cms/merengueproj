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

from merengue.base.models import Base, BaseContent


class Highlight(Base):
    weight = models.IntegerField(_('weight to decide ordering'), default=0)
    related_content = models.ForeignKey(BaseContent, verbose_name=_('related content'),
                                        null=True, blank=True)

    class Meta:
        ordering = ('-weight', )

    def get_absolute_url(self):
        if self.related_content:
            return self.related_content.get_absolute_url()
        else:
            return '#'
