from django.template import RequestContext
from django.template.loader import render_to_string

from merengue.registry.items import RegistrableItem
from merengue.viewlet.models import RegisteredViewlet
from merengue.registry.signals import item_registered


class Viewlet(RegistrableItem):
    label = None # to be overriden in subclasses
    model = RegisteredViewlet

    @classmethod
    def get_category(cls):
        return 'viewlet'

    @classmethod
    def render_viewlet(cls, request, template_name='viewlet.html', context=None):
        if context is None:
            context = {}
        viewlet_context = {
            'registered_viewlet': cls.get_registered_item(),
            'viewlet': cls,
        }
        viewlet_context.update(context)
        return render_to_string(template_name, viewlet_context,
                                context_instance=RequestContext(request))

    @classmethod
    def render(cls, request):
        raise NotImplementedError('You have to override this method')


def registered_viewlet(sender, **kwargs):
    if issubclass(sender, Viewlet):
        registered_item = kwargs['registered_item']
        registered_item.name = sender.name
        registered_item.save()


item_registered.connect(registered_viewlet)
