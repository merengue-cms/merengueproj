from django.core.exceptions import ObjectDoesNotExist

from merengue.registry.models import RegisteredItem
from merengue.registry.params import ConfigDict

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
        registered_item = cls.get_registered_item()
        return ConfigDict(cls.config_params, registered_item.get_config())

    @classmethod
    def get_registered_item(cls):
        for registered_item in cls.model.objects.all():
            # note: we do not use get to use cache from caching manager
            if registered_item.module == cls.get_module() and \
               registered_item.class_name == cls.get_class_name():
                return registered_item
        raise ObjectDoesNotExist

    @classmethod
    def get_extended_attrs(cls):
        return {}

"""
Example use::

class Action(RegistrableItem):
    model = RegisteredAction

    @classmethod
    def get_category(cls):
        return 'action'

class PDFExport(Action):
    name = "pdfexport"

    config_params = params.Single(name='pdfbin', default='/usr/bin/html2pdf')

>>> from merengue.pluggable.pdfexport.actions import PDFExport
>>> PDFExport.get_config()['pdfbin']
"""
