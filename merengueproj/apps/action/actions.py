from action.models import RegisteredAction
#from registry import params
from registry.items import RegistryItem


class BaseAction(RegistryItem):
    model = RegisteredAction

    @classmethod
    def get_category(cls):
        return 'action'

    # do some stuff


class SiteAction(BaseAction):
    pass


class UserAction(BaseAction):
    pass


class ContentAction(BaseAction):
    pass
