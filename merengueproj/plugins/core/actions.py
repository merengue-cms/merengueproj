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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import UserAction, SiteAction


class AdminAction(UserAction):
    name = 'admin'
    verbose_name = _('Admin site')

    @classmethod
    def get_url(cls, request, user):
        return reverse('admin_index')

    @classmethod
    def has_action(cls, user):
        return user.is_staff


class LoginAction(UserAction):
    name = 'login'
    verbose_name = _('Login')

    @classmethod
    def get_url(cls, request, user):
        login_url = reverse('merengue_login')
        if request.get_full_path() not in [reverse('merengue_logout'), reverse('admin:logout')]:  # to avoid automatic logout after login
            login_url += '?next=%s' % request.get_full_path()
        return login_url

    @classmethod
    def has_action(cls, user):
        return not user.is_authenticated()


class LogoutAction(UserAction):
    name = 'logout'
    verbose_name = _('Logout')

    @classmethod
    def get_url(cls, request, user):
        return reverse('merengue_logout')

    @classmethod
    def has_action(cls, user):
        return user.is_authenticated()


class PrintAction(SiteAction):
    name = 'print'
    verbose_name = _('Print')
