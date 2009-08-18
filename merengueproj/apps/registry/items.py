from registry.models import RegisteredItem


# ---- Exception definitions ----


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class RegistryError(Exception):
    pass


# ---- Base classes ----


class RegistryItem(object):
    """ Base class for all registered objects """

    name = None # to be overriden in subclasses
    model = RegisteredItem # to be overriden in subclasses
    config_params = [] # configuration parameters, to be overriden

    @classmethod
    def get_class_name(cls):
        return cls.__name__

    @classmethod
    def get_module(cls):
        return cls.__module__

    @classmethod
    def get_category(cls):
        return 'registryitem'

    @classmethod
    def get_config(cls):
        registered_item = cls.model.objects.get(
            name=cls.name,
            class_name=cls.get_class_name(),
        )
        return registered_item.config


"""
Example use::

class Action(RegistryItem):
    model = RegisteredAction

    @classmethod
    def get_category(cls):
        return 'action'

class PDFExport(Action):
    name = "pdfexport"


>>> from plugins.pdfexport.actions import PDFExport
>>> PDFExport.get_config('pdfbin')
"""
