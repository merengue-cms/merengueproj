from registry.models import RegisteredItem
from registry.params import ConfigList

# ---- Exception definitions ----


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class RegistryError(Exception):
    pass


# ---- Base classes ----


class RegistrableItem(object):
    """ Base class for all registered objects """

    name = None # to be overriden in subclasses
    model = None # to be overriden in subclasses
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
        registered_item = RegisteredItem.objects.get(
            class_name=cls.get_class_name(),
            module=cls.get_module(),
        )
        return ConfigList(cls.config_params, registered_item.config)


"""
Example use::

class Action(RegistrableItem):
    model = RegisteredAction

    @classmethod
    def get_category(cls):
        return 'action'

class PDFExport(Action):
    name = "pdfexport"


>>> from plugins.pdfexport.actions import PDFExport
>>> PDFExport.get_config('pdfbin')
"""
