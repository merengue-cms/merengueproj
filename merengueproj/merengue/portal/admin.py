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

from transmeta import get_fallback_fieldname

from merengue.base.admin import BaseAdmin
from merengue.portal.models import PortalLink
from merengue.portal.forms import PortalLinkForm
from merengue.perms import utils as perms_api


class PortalLinkAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ('category', )
    list_filter = ('visible_by_roles', 'category', )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}
    form = PortalLinkForm

    def has_add_permission(self, request):
        """
            Overrides Django admin behaviour to add ownership based access control
        """
        return perms_api.has_global_permission(request.user, 'manage_link')

    def has_change_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        return self.has_add_permission(request)


def register(site):
    site.register(PortalLink, PortalLinkAdmin)
