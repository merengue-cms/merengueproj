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

from merengue.action.actions import UserAction


class DashboardAction(UserAction):
    name = 'ezweb'
    verbose_name = _('dashboard')

    def get_url(self, request, user):
        return reverse('dashboard')

    def has_action(self, request, user):
        return user.is_authenticated()
