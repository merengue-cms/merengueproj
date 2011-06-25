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

from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.registration.actions import RegisterAction

from plugins.registration.models import Registration
from plugins.registration.admin import RegistrationAdmin


class PluginConfig(Plugin):
    name = 'Registration'
    description = 'Registration plugin'
    version = '0.0.1'

    url_prefixes = (
        ({'en': 'registration', 'es': 'registro'}, 'plugins.registration.urls'),
    )

    config_params = [
        params.PositiveInteger(name='caducity', label=_('hours before the registration url expires (0 for never)'), default=72),
        params.Single(name='profile_form_class', label=_('Form class to save extra profile data'), default="plugins.registration.forms.DefaultMerengueProfileForm"),
        ]

    def get_actions(self):
        return [RegisterAction]

    def models(self):
        return [(Registration, RegistrationAdmin)]
