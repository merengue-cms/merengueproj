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

from merengue.base.dbfields import JSONField
from merengue.pluggable.fields import (RequiredPluginsFormField,
                                       RequiredAppsFormField)


class RequiredPluginsField(JSONField):

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        kwargs['null'] = True
        super(RequiredPluginsField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': RequiredPluginsFormField}
        defaults.update(kwargs)
        return super(RequiredPluginsField, self).formfield(**defaults)


class RequiredAppsField(JSONField):

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        kwargs['null'] = True
        super(RequiredAppsField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': RequiredAppsFormField}
        defaults.update(kwargs)
        return super(RequiredAppsField, self).formfield(**defaults)
