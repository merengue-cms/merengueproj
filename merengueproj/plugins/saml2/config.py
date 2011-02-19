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

from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.saml2.models import IdentityProvider, ContactPerson, Organization
from plugins.saml2.admin import IdentityProviderAdmin, ContactPersonAdmin, OrganizationAdmin


class PluginConfig(Plugin):

    name = 'Saml2'
    description = 'Adds SAML2 authentication and authorization to Merengue'
    version = '0.1.0dev'

    url_prefixes = (
        ('saml2', 'plugins.saml2.urls'),
        )

    config_params = [
        params.Single(name='entity_id',
                      label=_('Entity ID')),
        params.Single(name='entity_name',
                      label=_('Entity Name')),
        params.Single(name='username_attribute',
                      label=_('Username attribute'),
                      default='uid'),
        params.Single(name='first_name_attribute',
                      label=_('First name attribute'),
                      default='cn'),
        params.Single(name='last_name_attribute',
                      label=_('First name attribute'),
                      default='sn'),
        params.Single(name='email_attribute',
                      label=_('Email attribute'),
                      default='mail'),
        params.Single(name='required_attributes',
                      label=_('Comma/space separated list of required attributes'),
                      default='uid'),
        params.Single(name='xmlsec_binary',
                      label=_('Path to xmlsec1 program'),
                      default='/usr/bin/xmlsec1'),
        params.Single(name='key_file_path',
                      label=_('Certificate private part')),
        params.Single(name='cert_file_path',
                      label=_('Certificate public part')),
        params.PositiveInteger(name='valid_for',
                               label=_('Expiration time in hours'),
                               default=24)
        ]

    def get_model_admins(self):
        return [
            (IdentityProvider, IdentityProviderAdmin),
            (ContactPerson, ContactPersonAdmin),
            (Organization, OrganizationAdmin),
            ]
