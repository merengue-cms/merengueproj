# Copyright (c) 2011 by Yaco Sistemas
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

#import saml2


class IdentityProvider(models.Model):

    BINDINGS = (
#        (saml2.BINDING_HTTP_REDIRECT, u'HTTP Redirect'),
        ('http-redirect', u'HTTP Redirect'),
        )

    entity_id = models.CharField(_('Entity ID'), max_length=200)

    single_sign_on_service_url = models.CharField(
        _('Single Sign On service url'),
        max_length=200,
        )

    single_sign_on_service_binding = models.CharField(
        _('Single Sign On service binding'),
        choices=BINDINGS,
        max_length=200,
        )

    single_logout_service_url = models.CharField(
        _('Single Logout service url'),
        max_length=200,
        )

    single_logout_service_binding = models.CharField(
        _('Single Logout service binding'),
        choices=BINDINGS,
        max_length=200,
        )

    metadata = models.TextField(_('XML Metadata'))

    def __unicode__(self):
        return self.entity_id


class ContactPerson(models.Model):

    CONTACT_TYPES = (
        ('technical', _(u'Technical')),
        ('administrative', _(u'Administrative')),
        )

    given_name = models.CharField(_('Given name'), max_length=200)
    sur_name = models.CharField(_('Sur name'), max_length=200)
    company = models.CharField(_('Company'), max_length=200)
    email_address = models.CharField(_('Email address'), max_length=200)
    contact_type = models.CharField(_('Contact type'), choices=CONTACT_TYPES,
                                    max_length=200)

    def __unicode__(self):
        return u'%s %s <%s>' % (self.given_name, self.sur_name, self.email_address)


class Organization(models.Model):

    name = models.CharField(_('Name'), max_length=200)
    display_name = models.CharField(_('Display name'), max_length=200)
    url = models.URLField(_('URL'), max_length=200)

    def __unicode__(self):
        return self.name
