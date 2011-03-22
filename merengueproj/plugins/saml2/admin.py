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

from django.contrib import admin

from plugins.saml2.models import IdentityProvider, ContactPerson, Organization


class IdentityProviderAdmin(admin.ModelAdmin):
    list_display = ('entity_id', 'single_sign_on_service_url',
                    'single_logout_service_url')


class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('given_name', 'sur_name', 'email_address')


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'url')


def register(site):
    """ Merengue admin registration callback """
    site.register(IdentityProvider, IdentityProviderAdmin)
    site.register(ContactPerson, ContactPersonAdmin)
    site.register(Organization, OrganizationAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(IdentityProvider)
    site.unregister(ContactPerson)
    site.unregister(Organization)
