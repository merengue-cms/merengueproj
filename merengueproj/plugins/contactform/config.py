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

from django.utils.translation import ugettext_lazy as _

from merengue.pluggable import Plugin
from merengue.registry import params

from plugins.contactform.models import ContactForm, SentContactForm
from plugins.contactform.admin import ContactFormAdmin, SentContactFormAdmin
from plugins.contactform.blocks import ContactFormBlock


class PluginConfig(Plugin):
    name = 'ContactForm'
    description = 'ContactForm plugin'
    version = '0.0.1'

    url_prefixes = (
        ({'en': 'contactform',
          'es': 'formulario_de_contacto'},
             'plugins.contactform.urls'),
    )

    config_params = [
        params.Single(name='rpubk', label=_('recaptcha public key'), default='6LegA8ASAAAAAF9AhuaPUPYb94p3vE4IkHOxfgAi'),
        params.Single(name='rprivk', label=_('recaptcha private key'), default='6LegA8ASAAAAAAI-nxu0DcCdDCQIzuWCNbKOXPw3'),
    ]

    def get_blocks(self):
        return [ContactFormBlock]

    def get_model_admins(self):
        return [(ContactForm, ContactFormAdmin),
                (SentContactForm, SentContactFormAdmin)]
