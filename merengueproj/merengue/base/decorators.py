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

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required as login_required_django

from merengue.base.utils import get_login_url
from merengue.perms.exceptions import PermissionDenied


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    return login_required_django(function,
                                 redirect_field_name=redirect_field_name,
                                 login_url=get_login_url())


def login_required_or_permission_denied(view_func):

    def _decorator(request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied(user=request.user)
        return view_func(request, *args, **kwargs)
    return _decorator
