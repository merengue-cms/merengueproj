from django.core.urlresolvers import reverse

from action.models import RegisteredAction
from merengue.registry.items import RegistrableItem


class BaseAction(RegistrableItem):
    model = RegisteredAction

    @classmethod
    def get_category(cls):
        return 'action'

    @classmethod
    def get_url(cls):
        return reverse("actions_dispatcher", args=(cls.name, ))

    @classmethod
    def get_extended_attrs(cls):
        return {'name': cls.name}


class SiteAction(BaseAction):
    pass


class UserAction(BaseAction):
    pass


class ContentAction(BaseAction):
    pass
