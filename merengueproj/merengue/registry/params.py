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

import copy

from django.template.loader import render_to_string
from django.utils import formats
from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str


class NotProvidedMeta(type):

    def __nonzero__(self):
        # we ensure when some param have not been defined (get a NOT_PROVIDED value)
        # evaluate to False, to avoid some logic errors. See #1307 ticket.
        return False


class NOT_PROVIDED:
    __metaclass__ = NotProvidedMeta

    def __nonzero__(self):
        # we ensure NOT_PROVIDED evaluates to False in Django 1.3 templates
        # if we do {% if foovalue %} and foovalue is NOT_PROVIDED class
        # Django templates in 1.3 will call to class creating a NOT_PROVIDED
        # object, which have to evaluate to false to avoid some logic errors
        return False


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
        value = self.get_value()
        if value == NOT_PROVIDED:
            return None
        else:
            return value

    def get_value_from_datadict(self, data, name):
        return data.get(name)

    def is_valid(self, value):
        """ returns if value is valid in this kind of param,
            to implement form validation """
        return True

    def render(self, name, widget_attrs,
               template_name='registry/param_widget.html',
               extra_context=None):
        # This method is to be implemented on children classes
        context = {'param': self, 'name': name, 'widget_attrs': widget_attrs}
        context.update(extra_context or {})
        return render_to_string(template_name, context)


class Single(Param):
    pass


class Parsed(Param):

    def get_parsed_value(self, value):
        raise NotImplementedError()

    def get_value(self):
        value = super(Parsed, self).get_value()
        return self.get_parsed_value(value)

    def get_value_from_datadict(self, data, name):
        value = super(Parsed, self).get_value_from_datadict(data, name)
        return self.get_parsed_value(value)


class Integer(Parsed):

    def get_parsed_value(self, value):
        if value is not None and isinstance(value, basestring) and value.strip('-').isdigit():
            try:
                return int(value)
            except ValueError:
                # return value if any error happends that will get validated
                pass
        return value

    def is_valid(self, value):
        return isinstance(value, int)


class PositiveInteger(Integer):

    def is_valid(self, value):
        return isinstance(value, int) and value >= 0


class Float(Parsed):

    def get_parsed_value(self, value):
        if value is not None and isinstance(value, basestring):
            value = formats.sanitize_separators(value)
            try:
                return float(value)
            except ValueError:
                # return value if any error happends that will get validated
                pass
        return value

    def is_valid(self, value):
        value = self.get_parsed_value(value)
        return isinstance(value, float)


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

    def is_valid(self, value):
        return isinstance(value, bool)

    def render(self, name, widget_attrs,
               template_name='registry/bool_widget.html',
               extra_context=None):
        return super(Bool, self).render(name, widget_attrs,
                                        template_name, extra_context)


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

    def render(self, name, widget_attrs,
               template_name='registry/list_widget.html',
               extra_context=None):
        return super(List, self).render(name, widget_attrs,
                                        template_name, extra_context)


class Content(PositiveInteger):

    def is_valid(self, value):
        from merengue.base.models import BaseContent  # import here to avoid circular imports
        return super(Content, self).is_valid(value) and \
               BaseContent.objects.filter(id=value)


class Text(Param):

    def render(self, name, widget_attrs,
               template_name='registry/text_widget.html',
               extra_context=None):
        return super(Text, self).render(name, widget_attrs,
                                        template_name, extra_context)


class ConfigDict(SortedDict):

    def __init__(self, config_params, config_values):
        super(ConfigDict, self).__init__()
        for param in config_params:
            param = copy.copy(param)
            if config_values and param.name in config_values:
                param.value = config_values[param.name]
            self[param.name] = param

    def update(self, d):
        for k, v in d.iteritems():
            if v.get_value() != NOT_PROVIDED:
                self[k] = v
