from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from merengue.action.models import RegisteredAction
from merengue.registry.items import RegistrableItem


class BaseAction(RegistrableItem):
    model = RegisteredAction

    @classmethod
    def get_category(cls):
        return 'action'

    @classmethod
    def get_url(cls, request):
        raise NotImplementedError()

    @classmethod
    def get_extended_attrs(cls):
        return {'name': cls.name}

    @classmethod
    def get_response(cls):
        raise NotImplementedError()

    @classmethod
    def has_action(cls):
        return True


class SiteAction(BaseAction):

    @classmethod
    def get_url(cls, request):
        return reverse("site_action", args=(cls.name, ))


class UserAction(BaseAction):

    @classmethod
    def has_action(cls, user):
        return super(UserAction, cls).has_action()

    @classmethod
    def get_url(cls, request, user):
        return reverse("user_action", args=(user.username, cls.name, ))


class ContentAction(BaseAction):

    @classmethod
    def get_url(cls, request, content):
        content_type = ContentType.objects.get_for_model(content.__class__)
        return reverse("content_action", args=(content_type.id, content.id, cls.name, ))

    @classmethod
    def get_response(cls, content):
        raise NotImplementedError()

    @classmethod
    def has_action(cls, content):
        return super(ContentAction, cls).has_action()
