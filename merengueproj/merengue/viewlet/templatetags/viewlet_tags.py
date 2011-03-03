# Copyright (c) 2010 by Yaco Sistemas
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

from django import template
from django.http import Http404
from django.core.exceptions import PermissionDenied
from merengue.base.utils import get_render_http_error

register = template.Library()


class RenderViewletNode(template.Node):

    def __init__(self, registered_viewlet):
        self.registered_viewlet = registered_viewlet

    def render(self, context):
        request = context.get('request', None)
        try:
            if self.registered_viewlet is not None:
                viewlet = self.registered_viewlet.resolve(context).get_registry_item()
            else:  # if no viewlet found
                return ''
            return viewlet.render(request, context)
        except template.VariableDoesNotExist:
            return ''
        except PermissionDenied:
            return get_render_http_error(request, 403)
        except Http404:
            return get_render_http_error(request, 404)


@register.tag(name='render_viewlet')
def do_render_viewlet(parser, token):
    """
    Usage::
      render_viewlet registered_viewlet
    """
    bits = token.split_contents()
    tag_name = bits[0]
    if len(bits) != 2:
        raise template.TemplateSyntaxError('"%r" tag requires at one argument' % tag_name)
    registered_viewlet = parser.compile_filter(bits[1])
    return RenderViewletNode(registered_viewlet)
