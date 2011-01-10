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

# permissions import
import merengue.perms.utils


class ObjectPermissionsBackend(object):
    """Django backend for object permissions. Needs Django 1.2.


    Use it together with the default ModelBackend like so::

        AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'permissions.backend.ObjectPermissionsBackend',
        )
    """
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        return None

    def has_permission(self, permission_codename, user, obj=None):
        """Checks whether the passed user has passed permission for passed
        object (obj).

        This should be the primary method to check wether a user has a certain
        permission.

        Parameters
        ==========

        permission
            The permission's codename which should be checked.

        user
            The user for which the permission should be checked.

        obj
            The object for which the permission should be checked.
        """
        return merengue.perms.utils.has_permission(obj, user, permission_codename)
