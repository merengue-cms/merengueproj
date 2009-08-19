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


class Single(Param):
    pass


class List(Param):
    pass


class Text(Param):
    pass


class ConfigDict(SortedDict):

    def __init__(self, config_params, config_values):
        super(ConfigDict, self).__init__()
        for param in config_params:
            if param.name in config_values:
                param.value = config_values[param.name]
            self[param.name] = param
