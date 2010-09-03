# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

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
            'template_base': 'viewlet.html',
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
