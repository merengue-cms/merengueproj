class NOT_PROVIDED:
    pass


class Param(object):
    """ Base class for all configuration parameters """

    def __init__(self, name=None, verbose_name=None, default=NOT_PROVIDED, choices=None):
        self.name = name
        self.verbose_name = verbose_name
        self.default = default
        self.choices = choices


class Single(Param):
    pass


class List(Param):
    pass


class Text(Param):
    pass
