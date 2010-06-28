# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str


class NOT_PROVIDED:
    pass


class Param(object):
    """ Base class for all configuration parameters """

    def __init__(self, name=None, label=None, default=NOT_PROVIDED, choices=None):
        self.name = name
        self.label = label
        self.default = default
        self.choices = choices

    def __repr__(self):
        return smart_str(unicode(self))

    def __unicode__(self):
        return u"<%s, %s>" % (self.get_value(), self.get_type())

    def has_default(self):
        return self.default is not NOT_PROVIDED

    def get_type(self):
        return self.__class__.__name__

    def get_value(self):
        return getattr(self, 'value', self.default)

    def get_value_display(self):
        return self.get_value()

    def get_value_from_datadict(self, data, name):
        return data.get(name)


class Single(Param):
    pass


class Integer(Param):

    def get_value(self):
        return int(super(Integer, self).get_value())

    def get_value_from_datadict(self, data, name):
        val = super(Integer, self).get_value_from_datadict(data, name)
        return int(val)


class Bool(Param):

    VAL_FALSE = ['false', 'none']

    def get_value(self):
        val = super(Bool, self).get_value()
        if not val or (getattr(val, 'lower', None) and val.lower() in self.VAL_FALSE):
            return False
        return bool(val)

    def get_value_from_datadict(self, data, name):
        val = super(Bool, self).get_value_from_datadict(data, name)
        if not val or (getattr(val, 'lower', None) and val.lower() in self.VAL_FALSE):
            return False
        return bool(val)


class List(Param):

    def get_value_display(self):
        value = self.get_value()
        return u'\n'.join(value)

    def get_value_from_datadict(self, data, name):
        values = data.getlist(name)
        value = []
        for v in values:
            value += v.split('\r\n')
        # delete empty lines
        value = [v for v in value if v.strip()]
        return value


class Text(Param):
    pass


class ConfigDict(SortedDict):

    def __init__(self, config_params, config_values):
        super(ConfigDict, self).__init__()
        for param in config_params:
            if param.name in config_values:
                param.value = config_values[param.name]
            self[param.name] = param
