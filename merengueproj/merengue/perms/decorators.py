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

from django.contrib.auth.decorators import user_passes_test

from merengue.perms.utils import has_permission


def permission_required(view_func=None, codename=None, roles=None, login_url=None):

    def _permission_required(user, *args, **kwargs):
        return has_permission(obj=None, user=user, codename=codename, roles=None)
    decorator = user_passes_test(_permission_required, login_url)
    if view_func:
        return decorator(view_func)
    return decorator
