_catalog = {}


def register(gadget_class):
    _catalog[gadget_class.name] = gadget_class


def unregister(gadget_class):
    del _catalog[gadget_class.name]


def get_by_name(name):
    return _catalog[name]


def get_list():
    return _catalog.items()
