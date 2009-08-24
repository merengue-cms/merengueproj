from block.models import RegisteredBlock
from registry.items import RegistrableItem
from registry.signals import item_registered


class BaseBlock(RegistrableItem):
    model = RegisteredBlock

    @classmethod
    def get_category(cls):
        return 'block'


class Block(BaseBlock):
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request):
        raise NotImplementedError()


class ContentBlock(BaseBlock):
    default_place = 'content'

    @classmethod
    def render(cls, request, content):
        raise NotImplementedError()


def registered_block(sender, **kwargs):
    if issubclass(sender, BaseBlock):
        registered_item = kwargs['registered_item']
        registered_item.placed_at = sender.default_place
        registered_item.name = sender.name
        registered_item.save()


item_registered.connect(registered_block)
