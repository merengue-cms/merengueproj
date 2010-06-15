from django.template import RequestContext
from django.template.loader import render_to_string

from merengue.block.models import RegisteredBlock
from merengue.registry.items import RegistrableItem
from merengue.registry.signals import item_registered


class BaseBlock(RegistrableItem):
    model = RegisteredBlock

    @classmethod
    def get_category(cls):
        return 'block'

    @classmethod
    def render_block(cls, request, template_name='block.html', block_title=None, context=None):
        if context is None:
            context = {}
        registered_block = cls.get_registered_item()
        block_context = {
            'block_title': block_title or registered_block.name,
            'block': registered_block,
        }
        block_context.update(context)
        return render_to_string(template_name, block_context,
                                context_instance=RequestContext(request))


class Block(BaseBlock):
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        raise NotImplementedError()


class ContentBlock(BaseBlock):
    default_place = 'content'

    @classmethod
    def render(cls, request, place, content, context, *args, **kwargs):
        raise NotImplementedError()


class SectionBlock(BaseBlock):
    default_place = 'leftsidebar'

    @classmethod
    def render(cls, request, place, section, context, *args, **kwargs):
        raise NotImplementedError()


def registered_block(sender, **kwargs):
    if issubclass(sender, BaseBlock):
        registered_item = kwargs['registered_item']
        registered_item.placed_at = sender.default_place
        registered_item.name = sender.name
        registered_item.save()


item_registered.connect(registered_block)
