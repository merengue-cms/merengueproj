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

import datetime

from django.db.models import Manager
from merengue.pluggable.utils import get_plugin


class RegistrationManager(Manager):

    def actives(self):
        plugin_config = get_plugin('registration').get_config()
        caducity = plugin_config.get('caducity').get_value()
        qs = self.all()
        if caducity:
            now = datetime.datetime.now()
            from_date = now - datetime.timedelta(hours=caducity)
            return qs.filter(registration_date__gte=from_date)
        return qs
