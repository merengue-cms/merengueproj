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

from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext


class BaseLocation(models.Model):

    main_location = models.PointField(verbose_name=_('main location'))

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def has_location(self):
        # a_float == a_float checks for nan values
        return not self.main_location is None and \
               self.main_location.x == self.main_location.x and \
               self.main_location.y == self.main_location.y

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self)
        return ('base.views.admin_link', [content_type.id, self.id, ''])


class Location(BaseLocation):
    address = models.CharField(verbose_name=_('address'),
                               max_length=250, blank=True, null=True)
    postal_code = models.CharField(verbose_name=_('postal_code'),
                                   max_length=100, blank=True, null=True)

    objects = models.GeoManager()

    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    def __unicode__(self):
        if self.address:
            return self.address
        elif self.main_location:
            return self.main_location.wkt
        else:
            return ugettext('Without localization')

    def complete_address(self):
        comp_add = u''
        comp_add = self.address and u'%s %s' % (comp_add, self.address) or comp_add
        comp_add = self.postal_code and u'%s C.P. %s' % (comp_add, self.postal_code) or comp_add
        return comp_add.strip()
    complete_address.short_description = _('Address')
