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

from plugins.registration.managers import RegistrationManager


class Registration(models.Model):
    """ A registration """
    username = models.CharField(
        _('username'),
        max_length=30,
        help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"),
        )
    email = models.EmailField(
        _('e-mail address'),
        )
    registration_date = models.DateTimeField(
        _('Registration date'),
        auto_now_add=True,
        )
    registration_hash = models.CharField(
        max_length=32,
        )

    objects = RegistrationManager()

    class Meta:
        verbose_name = _('registration')
        verbose_name_plural = _('registrations')
        ordering = ('-registration_date', )

    def __unicode__(self):
        return u'%s <%s>' % (self.username, self.email)
