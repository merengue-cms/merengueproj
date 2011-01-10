# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ImageSize(models.Model):

    folder = models.CharField(verbose_name=_('folder'), max_length=200)
    max_width = models.IntegerField(verbose_name=_('max width'))
    max_height = models.IntegerField(verbose_name=_('max height'))
    recipients = models.ManyToManyField(User,
                                verbose_name=_('notification recipients'))
    notified = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.folder
