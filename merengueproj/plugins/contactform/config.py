# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

from merengue.pluggable import Plugin

from plugins.contactform.models import ContactForm, ContactFormOpt
from plugins.contactform.admin import ContactFormAdmin
from plugins.contactform.blocks import ContactFormBlock


class PluginConfig(Plugin):
    name = 'ContactForm'
    description = 'ContactForm plugin'
    version = '0.0.1'

    url_prefixes = (
        ('contactform', 'plugins.contactform.urls'),
    )

    @classmethod
    def get_blocks(cls):
        return [ContactFormBlock]

    @classmethod
    def get_model_admins(cls):
        return [(ContactForm, ContactFormAdmin),]
