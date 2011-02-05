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

from django.forms import ValidationError
from django.utils.translation import ugettext as _

from cmsutils.forms.fields import JSONFormField

from merengue.registry.widgets import ConfigWidget


class ConfigFormField(JSONFormField):

    def __init__(self, *args, **kwargs):
        super(ConfigFormField, self).__init__(*args, **kwargs)
        self.label = kwargs.get('label', _('Configuration'))
        self.widget = ConfigWidget()

    def set_config(self, config):
        self.config = config
        self.widget.add_config_widgets(config)

    def clean(self, value):
        value = super(ConfigFormField, self).clean(value)
        for name, param in self.config.items():
            if not param.is_valid(value.get(name, None)):
                raise ValidationError(_('Error in "%(name)s" field') % {'name': param.label})
        return value
