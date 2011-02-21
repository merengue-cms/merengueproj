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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import UserAction


class Saml2LoginAction(UserAction):
    name = 'saml2_login'
    verbose_name = _('Federated login')

    @classmethod
    def get_url(cls, request, user):
        return reverse('saml2_login')

    @classmethod
    def has_action(cls, user):
        return not user.is_authenticated()


class Saml2LogoutAction(UserAction):
    name = 'saml2_logout'
    verbose_name = _('Federated logout')

    @classmethod
    def get_url(cls, request, user):
        return reverse('saml2_logout')

    @classmethod
    def has_action(cls, user):
        return user.is_authenticated()
