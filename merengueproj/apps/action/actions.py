from action.models import RegisteredAction
from registry.items import RegistrableItem


class BaseAction(RegistrableItem):
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
